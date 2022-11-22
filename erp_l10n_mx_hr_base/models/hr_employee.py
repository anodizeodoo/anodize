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
    _inherit = ['mail.thread']

    name = fields.Char(
        help='Value to set in the "RegistroPatronal" attribute.', tracking=True)
    job_risk_id = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', required=True, tracking=True)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_mx_edi_syndicated = fields.Boolean(
        'Syndicated', help='Used in the XML to indicate if the worker is '
        'associated with a union. If it is omitted, it is assumed that it is '
        'not associated with any union.', tracking=True)
    l10n_mx_edi_risk_rank = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', tracking=True)
    l10n_mx_edi_contract_regime_type_id = fields.Many2one('l10n.mx.edi.contract.regime.type',
                                                          tracking=True,
                                                          string='Regime Type')
    l10n_mx_edi_is_assimilated = fields.Boolean(
        'Is assimilated?',
        tracking=True,
        help='If this employee is assimilated, must be '
        'used this option, to get the correct rules on their payslips')
    l10n_mx_edi_employer_registration_id = fields.Many2one(
        'l10n_mx_payroll.employer.registration', 'Employer Registration',
        tracking=True,
        help='If the company has multiple employer registration, define the '
        'correct for this employee.')
    l10n_mx_edi_rfc = fields.Char(related='address_home_id.vat',
                                  string='RFC',
                                  readonly=False,
                                  store=True,
                                  compute_sudo=True)
    l10n_mx_edi_curp = fields.Char(related='address_home_id.l10n_mx_edi_curp',
                                   string='CURP',
                                   readonly=False,
                                   store=True,
                                   compute_sudo=True)
    l10n_mx_edi_family_medical_unit = fields.Char(string='Family Medical Unit', tracking=True)
    l10n_mx_edi_afore_number = fields.Char(string='Afore Number', tracking=True)
    l10n_mx_payment_method = fields.Selection([('PUE', '(PUE) Pago en una sola exhibición'),
                                               ('PPD', '(PPD) Pago en parcialidades o diferido')],
                                              tracking=True,
                                               default='PUE', string="Payment method")

    zip = fields.Char(string='C.P', related='address_home_id.zip', compute_sudo=True)
    age = fields.Char('Age', compute="_compute_age")
    bank_id = fields.Many2one('res.bank', string='Bank', tracking=True)
    l10n_mx_edi_clabe = fields.Char("CLABE", tracking=True)
    filtered_banks = fields.One2many(comodel_name='res.bank', compute='_filter_banks')

    @api.depends('birthday')
    def _compute_age(self):
        for record in self:
            record.age = relativedelta(fields.Date.today(), record.birthday).years

    @api.depends('address_home_id')
    def _filter_banks(self):
        for bank in self:
            bank.filtered_banks = bank.address_home_id.bank_ids.mapped('bank_id')

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

    @api.model
    def create(self, vals):
        if vals.get('firstname'):
            vals.update({'firstname': self._get_return_without_accent(vals.get('firstname')).upper()})
        if vals.get('lastname'):
            vals.update({'lastname': self._get_return_without_accent(vals.get('lastname')).upper()})
        if vals.get('lastname2'):
            vals.update({'lastname2': self._get_return_without_accent(vals.get('lastname2')).upper()})
        return super(HrEmployee, self).create(vals)

    def write(self, vals):
        if vals.get('firstname'):
            vals.update({'firstname': self._get_return_without_accent(vals.get('firstname')).upper()})
        if vals.get('lastname'):
            vals.update({'lastname': self._get_return_without_accent(vals.get('lastname')).upper()})
        if vals.get('lastname2'):
            vals.update({'lastname2': self._get_return_without_accent(vals.get('lastname2')).upper()})
        return super(HrEmployee, self).write(vals)

    def action_update_employee_name(self):
        for record in self:
            record.firstname = self._get_return_without_accent(record.firstname).upper()
            record.lastname = self._get_return_without_accent(record.lastname).upper()
            record.lastname2 = self._get_return_without_accent(record.lastname2).upper()

