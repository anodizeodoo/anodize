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

from lxml import etree, objectify
from werkzeug import url_encode
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)

class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']

    l10n_mx_extra_node_ids = fields.One2many(
        'hr.payslip.extra.perception', 'payslip_id',
        string='Extra data to perceptions',
        help='If the payslip have perceptions with code in 022, 023 or 025,'
             'must be created a record with data that will be assigned in the '
             'node "SeparacionIndemnizacion", or if the payslip have perceptions '
             'with code in 039 or 044 must be created a record with data that will '
             'be assigned in the node "JubilacionPensionRetiro". Only must be '
             'created a record by node.')

    l10n_mx_action_title_ids = fields.One2many(
        'hr.payslip.action.titles', 'payslip_id', string='Action or Titles',
        help='If the payslip have perceptions with code 045, assign here the '
        'values to the attribute in XML, use the perception type to indicate '
        'if apply to exempt or taxed.')

    l10n_mx_payment_date = fields.Date(
        'Payment Date', required=True, readonly=True,
        states={'draft': [('readonly', False)]},
        default=time.strftime('%Y-%m-01'), help='Save the payment date that '
                                                'will be added on CFDI.')
    l10n_mx_cfdi_name = fields.Char(
        string='CFDI name', copy=False, readonly=True,
        help='The attachment name of the CFDI.')

    l10n_mx_pac_status = fields.Selection(
        [('retry', 'Retry'),
         ('to_sign', 'To sign'),
         ('signed', 'Signed'),
         ('to_cancel', 'To cancel'),
         ('cancelled', 'Cancelled')], 'PAC status',
        help='Refers to the status of the payslip inside the PAC.',
        readonly=True, copy=False)

    l10n_mx_sat_status = fields.Selection(
        [('none', 'State not defined'),
         ('undefined', 'Not Synced Yet'),
         ('not_found', 'Not Found'),
         ('cancelled', 'Cancelled'),
         ('valid', 'Valid')], 'SAT status',
        help='Refers to the status of the payslip inside the SAT system.',
        readonly=True, copy=False, required=True, tracking=True,
        default='undefined')

    l10n_mx_balance_favor = fields.Float(
        'Balance in Favor', help='If the payslip include other payments, and '
                                 'one of this records have the code 004 is need add the balance in '
                                 'favor to assign in node "CompensacionSaldosAFavor".')

    l10n_mx_comp_year = fields.Integer(
        'Year', help='If the payslip include other payments, and '
                     'one of this records have the code 004 is need add the year to assign '
                     'in node "CompensacionSaldosAFavor".')

    l10n_mx_remaining = fields.Float(
        'Remaining', help='If the payslip include other payments, and '
                          'one of this records have the code 004 is need add the remaining to '
                          'assign in node "CompensacionSaldosAFavor".')

    l10n_mx_source_resource = fields.Selection([
        ('IP', 'Own income'),
        ('IF', 'Federal income'),
        ('IM', 'Mixed income')], 'Source Resource',
        help='Used in XML to identify the source of the resource used '
             'for the payment of payroll of the personnel that provides or '
             'performs a subordinate or assimilated personal service to salaries '
             'in the dependencies. This value will be set in the XML attribute '
             '"OrigenRecurso" to node "EntidadSNCF".')

    l10n_mx_amount_sncf = fields.Float(
        'Own resource', help='When the attribute in "Source Resource" is "IM" '
                             'this attribute must be added to set in the XML attribute '
                             '"MontoRecursoPropio" in node "EntidadSNCF", and must be less that '
                             '"TotalPercepciones" + "TotalOtrosPagos"')

    l10n_mx_cfdi_string = fields.Char(
        'CFDI Original String', help='Attribute "cfdi_cadena_original" '
                                     'returned by PAC request when is stamped the CFDI, this attribute is '
                                     'used on report.')

    l10n_mx_origin = fields.Char(
        string='CFDI Origin', copy=False,
        help='In some cases the payroll must be regenerated to fix data in it.'
             ' In that cases is necessary this field filled, the format is: '
             '\n04|UUID1, UUID2, ...., UUIDn.\n'
             'Example:\n"04|89966ACC-0F5C-447D-AEF3-3EED22E711EE,'
             '89966ACC-0F5C-447D-AEF3-3EED22E711EE"')

    l10n_mx_expedition_date = fields.Date(
        string='Payslip date', readonly=True, copy=False, index=True,
        states={'draft': [('readonly', False)]},
        help="Keep empty to use the current date")

    l10n_mx_time_payslip = fields.Char(
        string='Time payslip', readonly=True, copy=False,
        states={'draft': [('readonly', False)]},
        help="Keep empty to use the current México central time")

    sent = fields.Boolean(readonly=True, default=False, copy=False,
                          help="It indicates that the payslip has been sent.")
    # Add parameter copy=True
    input_line_ids = fields.One2many(copy=True)

    l10n_mx_payslip_type = fields.Selection([('O', 'O-Ordinary Payroll'), ('E', 'E-Extraordinary')],
                                            string='Type of payroll')

    def l10n_mx_is_last_payslip(self):
        """Check if the date to in the payslip is the last of the current month
        and return True in that case, to know that is the last payslip"""
        if not self:
            return False
        self.ensure_one()
        if not self.date_to:
            return False
        if self.sudo().date_to.day == monthrange(
                self.sudo().date_to.year, self.sudo().date_to.month)[1]:
            return True
        return False

    @api.onchange('struct_id')
    def _onchange_struct_id(self):
        if self.struct_id:
            self.l10n_mx_payslip_type = self.sudo().struct_id.l10n_mx_payslip_type

    def _set_isr_negative(self, isr):
        if isr > 0:
            isr = isr * -1
        return isr

    def compute_sheet(self):
        super(HrPayslip, self).compute_sheet()
        for record in self:
            if not record.sudo().contract_id.l10n_mx_payroll_schedule_pay_id.l10n_mx_table_isr_id:
                raise ValidationError(_('The payment period in the contract %s must have to which ISR belongs.'
                                        % (record.sudo().contract_id.name)))
            total_rules_graba_isr = sum(record.sudo().line_ids.filtered(lambda r:
                                                                 r.salary_rule_id.l10n_mx_isr is True).mapped('amount'))
            print("Total Gravable ISR", total_rules_graba_isr)
            period_taxable = (record.sudo().contract_id.l10n_mx_payroll_schedule_pay_id.day_payment
                              * record.sudo().contract_id.l10n_mx_payroll_daily_salary) + total_rules_graba_isr
            l10n_mx_table_isr_rate_id = record.sudo().contract_id.l10n_mx_payroll_schedule_pay_id.\
                l10n_mx_table_isr_id.find_rule_by_rate(period_taxable)
            print("Period Taxable", period_taxable, l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_lower_limit,
                  l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_upper_limit, record.contract_id.l10n_mx_payroll_schedule_pay_id.name)
            exceed_lower_limit = period_taxable - l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_lower_limit
            print("Rate percentage", l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_percentage)
            rate_percentage = l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_percentage
            marginal_tax = (exceed_lower_limit * rate_percentage)/100
            print("Marginal tax", marginal_tax)
            rate_fixed_fee = l10n_mx_table_isr_rate_id.l10n_mx_isr_rate_fixed_fee
            print("Rate fixed fee", rate_fixed_fee)
            isr = marginal_tax + rate_fixed_fee
            l10n_mx_table_isr_subsidy_rate_id = record.sudo().contract_id.l10n_mx_payroll_schedule_pay_id.\
                l10n_mx_table_isr_id.find_rule_by_subsidy(period_taxable)
            isr_total = isr - l10n_mx_table_isr_subsidy_rate_id.l10n_mx_isr_subsidy_quantity
            print("ISR Subsidy Quantity", l10n_mx_table_isr_subsidy_rate_id.l10n_mx_isr_subsidy_quantity)
            line_isr_id = record.line_ids.filtered(lambda r: r.sudo().salary_rule_id.code == '002')
            if line_isr_id.salary_rule_id.l10n_mx_automatic_isr:
                line_isr_id.write({'amount': self._set_isr_negative(isr_total), 'quantity': 1.0})
                # line_isr_id._compute_total()
            line_aux_isr_id = record.line_ids.filtered(lambda r: r.sudo().salary_rule_id.code == 'AUX_ISR')
            if line_aux_isr_id.sudo().salary_rule_id.l10n_mx_automatic_isr:
                line_aux_isr_id.write({'amount': self._set_isr_negative(isr), 'quantity': 1.0})
                # line_aux_isr_id._compute_total()
            line_aux_op002_id = record.line_ids.filtered(lambda r: r.sudo().salary_rule_id.code == 'AUX_OP002')
            if line_aux_op002_id.sudo().salary_rule_id.l10n_mx_automatic_isr:
                line_aux_op002_id.write({'amount': self._set_isr_negative(l10n_mx_table_isr_subsidy_rate_id.l10n_mx_isr_subsidy_quantity), 'quantity': 1.0})
                # line_aux_op002_id._compute_total()
        return True


class HrPayslipActionTitles(models.Model):
    _name = 'hr.payslip.action.titles'
    _description = 'Pay Slip action titles'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    category_id = fields.Many2one(
        'hr.salary.rule.category', 'Category', required=True,
        help='Indicate to which perception will be added this attributes in '
        'node XML')
    market_value = fields.Float(
        help='When perception type is 045 this value must be assigned in the '
        'line. Will be used in node "AccionesOTitulos" to the attribute '
        '"ValorMercado"', required=True)
    price_granted = fields.Float(
        help='When perception type is 045 this value must be assigned in the '
        'line. Will be used in node "AccionesOTitulos" to the attribute '
        '"PrecioAlOtorgarse"', required=True)

class HrPayslipExtraPerception(models.Model):
    _name = 'hr.payslip.extra.perception'
    _description = 'Pay Slip extra perception'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    node = fields.Selection(
        [('retirement', 'JubilacionPensionRetiro'),
         ('separation', 'SeparacionIndemnizacion')], help='Indicate what is '
        'the record purpose, if will be used to add in node '
        '"JubilacionPensionRetiro" or in "SeparacionIndemnizacion"')
    amount_total = fields.Float(
        help='If will be used in the node "JubilacionPensionRetiro" and '
        'will be used to one perception with code "039", will be used to '
        'the attribute "TotalUnaExhibicion", if will be used to one '
        'perception with code "044", will be used to the attribute '
        '"TotalParcialidad". If will be used in the node '
        '"SeparacionIndemnizacion" will be used in attribute "TotalPagado"')
    amount_daily = fields.Float(
        help='Used when will be added in node "JubilacionPensionRetiro", to '
        'be used in attribute "MontoDiario"')
    accumulable_income = fields.Float(
        help='Used to both nodes, each record must be have the valor to each '
        'one.')
    non_accumulable_income = fields.Float(
        help='Used to both nodes, each record must be have the valor to each '
        'one.')
    service_years = fields.Integer(
        help='Used when will be added in node "SeparacionIndemnizacion", to '
        'be used in attribute "NumAñosServicio"')
    last_salary = fields.Float(
        help='Used when will be added in node "SeparacionIndemnizacion", to '
        'be used in attribute "UltimoSueldoMensOrd"')

class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    l10n_mx_payment_date = fields.Date(
        'Payment Date', required=True,
        default=time.strftime('%Y-%m-01'), help='Save the payment date that '
        'will be added on all payslip created with this batch.')
    l10n_mx_productivity_bonus = fields.Float(
        'Productivity Bonus', help='The amount to distribute to the employees in the payslips.')