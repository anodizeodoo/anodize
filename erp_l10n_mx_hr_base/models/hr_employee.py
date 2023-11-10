# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import base64
import logging
import re
import time
from io import BytesIO
from itertools import groupby
from calendar import monthrange
import requests
from dateutil.relativedelta import relativedelta
from unicodedata import normalize
from lxml import etree, objectify

from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)


class L10nMxPayrollEmployerRegistration(models.Model):
    _name = 'l10n_mx_payroll.employer.registration'
    _description = 'Allow define all the employer registration from the company'
    _inherit = ['mail.thread', 'format.address.mixin']

    name = fields.Char(string="Employer Register",
        help='Value to set in the "RegistroPatronal" attribute.',
        tracking=True, index=True)
    job_risk_id = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.',
        required=True,
        tracking=True, index=True)
    date_start = fields.Date(string='Date Start', tracking=True, index=True)
    date_end = fields.Date(string='Date End', tracking=True, index=True)
    active = fields.Boolean('Status', default=True, tracking=True, index=True)

    # Address fields
    street_name = fields.Char(
        'Street Name', compute='_compute_street_data',
        inverse='_inverse_street_data',
        store=True, tracking=True, index=True)
    street = fields.Char(tracking=True, index=True)
    street2 = fields.Char(tracking=True, index=True)
    zip = fields.Char(change_default=True, tracking=True, index=True)
    city = fields.Char(tracking=True, index=True)
    state_id = fields.Many2one("res.country.state",
                               string='State',
                               ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]",
                               tracking=True, index=True)
    country_id = fields.Many2one('res.country',
                                 string='Country',
                                 ondelete='restrict',
                                 tracking=True, index=True)
    street_number = fields.Char(
        'House',
        compute='_compute_street_data', inverse='_inverse_street_data',
        store=True, index=True)
    street_number2 = fields.Char(
        'Door', compute='_compute_street_data',
        inverse='_inverse_street_data',
        store=True, index=True)
    country_enforce_cities = fields.Boolean(related='country_id.enforce_cities',
                                            readonly=True, compute_sudo=True)
    city_id = fields.Many2one('res.city', string='City of Address', tracking=True, index=True)

    l10n_mx_edi_colony = fields.Char(
        string="Colony Name", tracking=True, index=True)
    l10n_mx_edi_colony_code = fields.Char(
        string="Colony Code",
        tracking=True,
        index=True,
        help="Note: Only use this field if this partner is the company address or if it is a branch office.\n"
             "Colony code that will be used in the CFDI with the external trade as Emitter colony. It must be a code "
             "from the SAT catalog.")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if rec.name and not rec.name.isalnum():
                raise ValidationError(_('The Name field must only contain alphanumeric characters (letters and numbers, but no special characters).'))

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id

    def _inverse_street_data(self):
        """Updates the street field.
        Writes the `street` field on the regpats when one of the sub-fields in STREET_FIELDS
        has been touched"""
        street_fields = self._get_street_fields()
        for regpat in self:
            street_format = (regpat.country_id.address_format or
                '%(street_number)s/%(street_number2)s %(street_name)s')
            previous_field = None
            previous_pos = 0
            street_value = ""
            separator = ""
            # iter on fields in street_format, detected as '%(<field_name>)s'
            for re_match in re.finditer(r'%\(\w+\)s', street_format):
                # [2:-2] is used to remove the extra chars '%(' and ')s'
                field_name = re_match.group()[2:-2]
                field_pos = re_match.start()
                if field_name not in street_fields:
                    raise UserError(_("Unrecognized field %s in street format.", field_name))
                if not previous_field:
                    # first iteration: add heading chars in street_format
                    if regpat[field_name]:
                        street_value += street_format[0:field_pos] + regpat[field_name]
                else:
                    # get the substring between 2 fields, to be used as separator
                    separator = street_format[previous_pos:field_pos]
                    if street_value and regpat[field_name]:
                        street_value += separator
                    if regpat[field_name]:
                        street_value += regpat[field_name]
                previous_field = field_name
                previous_pos = re_match.end()

            # add trailing chars in street_format
            street_value += street_format[previous_pos:]
            regpat.street = street_value

    @api.depends('street')
    def _compute_street_data(self):
        """Splits street value into sub-fields.
        Recomputes the fields of STREET_FIELDS when `street` of a regpat is updated"""
        street_fields = self._get_street_fields()
        for regpat in self:
            if not regpat.street:
                for field in street_fields:
                    regpat[field] = None
                continue

            street_format = (regpat.country_id.street_format or
                '%(street_number)s/%(street_number2)s %(street_name)s')
            street_raw = regpat.street
            vals = self._split_street_with_params(street_raw, street_format)
            # assign the values to the fields
            for k, v in vals.items():
                regpat[k] = v
            for k in set(street_fields) - set(vals):
                regpat[k] = None

    def _split_street_with_params(self, street_raw, street_format):
        street_fields = self._get_street_fields()
        vals = {}
        previous_pos = 0
        field_name = None
        # iter on fields in street_format, detected as '%(<field_name>)s'
        for re_match in re.finditer(r'%\(\w+\)s', street_format):
            field_pos = re_match.start()
            if not field_name:
                #first iteration: remove the heading chars
                street_raw = street_raw[field_pos:]

            # get the substring between 2 fields, to be used as separator
            separator = street_format[previous_pos:field_pos]
            field_value = None
            if separator and field_name:
                #maxsplit set to 1 to unpack only the first element and let the rest untouched
                tmp = street_raw.split(separator, 1)
                if previous_greedy in vals:
                    # attach part before space to preceding greedy field
                    append_previous, sep, tmp[0] = tmp[0].rpartition(' ')
                    street_raw = separator.join(tmp)
                    vals[previous_greedy] += sep + append_previous
                if len(tmp) == 2:
                    field_value, street_raw = tmp
                    vals[field_name] = field_value
            if field_value or not field_name:
                previous_greedy = None
                if field_name == 'street_name' and separator == ' ':
                    previous_greedy = field_name
                # select next field to find (first pass OR field found)
                # [2:-2] is used to remove the extra chars '%(' and ')s'
                field_name = re_match.group()[2:-2]
            else:
                # value not found: keep looking for the same field
                pass
            if field_name not in street_fields:
                raise UserError(_("Unrecognized field %s in street format.", field_name))
            previous_pos = re_match.end()

        # last field value is what remains in street_raw minus trailing chars in street_format
        trailing_chars = street_format[previous_pos:]
        if trailing_chars and street_raw.endswith(trailing_chars):
            vals[field_name] = street_raw[:-len(trailing_chars)]
        else:
            vals[field_name] = street_raw
        return vals

    def write(self, vals):
        res = super(L10nMxPayrollEmployerRegistration, self).write(vals)
        if 'country_id' in vals and 'street' not in vals:
            self._inverse_street_data()
        return res

    def _formatting_address_fields(self):
        """Returns the list of address fields usable to format addresses."""
        return super(Partner, self)._formatting_address_fields() + self._get_street_fields()

    def _get_street_fields(self):
        """Returns the fields that can be used in a street format.
        Overwrite this function if you want to add your own fields."""
        return ['street_name', 'street_number', 'street_number2']

    @api.onchange('city_id')
    def _onchange_city_id(self):
        if self.city_id:
            self.city = self.city_id.name
            self.zip = self.city_id.zipcode
            self.state_id = self.city_id.state_id
        elif self._origin:
            self.city = False
            self.zip = False
            self.state_id = False

    @api.model
    def _address_fields(self):
        """Returns the list of address fields that are synced from the parent."""
        return super(Partner, self)._address_fields() + ['city_id',]

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_mx_edi_syndicated = fields.Boolean(
        'Syndicated', help='Used in the XML to indicate if the worker is '
        'associated with a union. If it is omitted, it is assumed that it is '
        'not associated with any union.', tracking=True, index=True)
    l10n_mx_edi_risk_rank = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', tracking=True, index=True)
    percentage = fields.Float(related='l10n_mx_edi_risk_rank.percentage', compute_sudo=True)
    l10n_mx_edi_contract_regime_type_id = fields.Many2one('l10n.mx.edi.contract.regime.type',
                                                          tracking=True, index=True,
                                                          string='Regime Type')

    l10n_mx_edi_employee_type_id = fields.Many2one('l10n.mx.hr.employee.type',
                                                          tracking=True,
                                                          index=True,
                                                          string='Clasificador de Empleado')

    l10n_mx_edi_is_assimilated = fields.Boolean(
        'Is assimilated?',
        tracking=True,
        index = True,
        help='If this employee is assimilated, must be '
        'used this option, to get the correct rules on their payslips')
    l10n_mx_edi_employer_registration_id = fields.Many2one(
        'l10n_mx_payroll.employer.registration', 'Employer Registration',
        tracking=True,
        index=True,
        help='If the company has multiple employer registration, define the '
        'correct for this employee.')
    l10n_mx_edi_rfc = fields.Char(string='RFC', index=True, size=13)
    l10n_mx_edi_curp = fields.Char(string='CURP', index=True)
    l10n_mx_edi_family_medical_unit = fields.Char(string='Family Medical Unit', tracking=True, index=True)
    l10n_mx_edi_afore_number = fields.Char(string='Afore Number', tracking=True, index=True)
    l10n_mx_payment_method = fields.Selection([('PUE', '(PUE) Pago en una sola exhibición'),
                                               ('PPD', '(PPD) Pago en parcialidades o diferido')],
                                              tracking=True,
                                              index=True,
                                              default='PUE',
                                              string="Payment method")

    zip = fields.Char(string='C.P', index=True)
    email = fields.Char(string='Email', index=True)
    phone_employee = fields.Char(string='Phone', index=True)
    age = fields.Char('Age', compute="_compute_age")
    bank_id = fields.Many2one('res.bank', string='Bank', tracking=True, index=True)
    bank_account = fields.Char(string='Bank Account Number', index=True)
    l10n_mx_edi_clabe = fields.Char("CLABE", tracking=True, index=True)
    # filtered_banks = fields.One2many(comodel_name='res.bank', compute='_filter_banks')

    contact_ids = fields.One2many('res.partner', related='address_home_id.child_ids',
                                  readonly=False, compute_sudo=True)

    @api.constrains('ssnid')
    def _check_ssnid(self):
        for rec in self:
            if rec.ssnid and not rec.ssnid.isalnum():
                raise ValidationError(_('The Social Security Number field must only contain alphanumeric characters (letters and numbers, but no special characters).'))

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            record.age = relativedelta(fields.Date.today(), record.birthday).years

    # @api.depends('address_home_id')
    # def _filter_banks(self):
    #     for bank in self:
    #         bank.filtered_banks = bank.address_home_id.bank_ids.mapped('bank_id')

    @api.onchange('l10n_mx_edi_employer_registration_id')
    def _onchange_l10n_mx_edi_employer_registration_id(self):
        if self.l10n_mx_edi_employer_registration_id:
            self.l10n_mx_edi_risk_rank = self.l10n_mx_edi_employer_registration_id.job_risk_id.id

    @api.onchange('bank_id', 'address_home_id', 'bank_account_id')
    def _onchange_bank_id(self):
        if self.address_home_id and self.bank_id and self.bank_account_id:
            bank_ids = self.address_home_id.bank_ids.filtered(lambda b: b.bank_id == self.bank_id and b.acc_number == self.bank_account_id.acc_number)
            if bank_ids:
                self.l10n_mx_edi_clabe = bank_ids[0].l10n_mx_edi_clabe

    def _get_return_without_accent(self, word):
        word = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", normalize("NFD", word), 0, re.I)
        word = normalize('NFC', word)
        return word

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('firstname'):
                vals.update({'firstname': self._get_return_without_accent(vals.get('firstname')).upper()})
            if vals.get('lastname'):
                vals.update({'lastname': self._get_return_without_accent(vals.get('lastname')).upper()})
            if vals.get('lastname2'):
                vals.update({'lastname2': self._get_return_without_accent(vals.get('lastname2')).upper()})
            if vals.get('l10n_mx_edi_rfc'):
                vals.update({'l10n_mx_edi_rfc': vals.get('l10n_mx_edi_rfc').upper()})
            if vals.get('l10n_mx_edi_curp'):
                vals.update({'l10n_mx_edi_curp': vals.get('l10n_mx_edi_curp').upper()})
        return super(HrEmployee, self).create(vals_list)

    def write(self, vals):
        if vals.get('firstname'):
            vals.update({'firstname': self._get_return_without_accent(vals.get('firstname')).upper()})
        if vals.get('lastname'):
            vals.update({'lastname': self._get_return_without_accent(vals.get('lastname')).upper()})
        if vals.get('lastname2'):
            vals.update({'lastname2': self._get_return_without_accent(vals.get('lastname2')).upper()})
        if vals.get('l10n_mx_edi_rfc'):
            vals.update({'l10n_mx_edi_rfc': vals.get('l10n_mx_edi_rfc').upper()})
        if vals.get('l10n_mx_edi_curp'):
            vals.update({'l10n_mx_edi_curp': vals.get('l10n_mx_edi_curp').upper()})
        return super(HrEmployee, self).write(vals)

    def action_update_employee_name(self):
        for record in self:
            record.firstname = self._get_return_without_accent(record.firstname).upper()
            record.lastname = self._get_return_without_accent(record.lastname).upper()
            record.lastname2 = self._get_return_without_accent(record.lastname2).upper()

