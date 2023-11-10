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
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)

class HrContract(models.Model):
    _inherit = "hr.contract"

    loan_ids = fields.One2many(
        'hr.employee.loan', 'contract_id', 'Loans', context={'active_test': False},
        help='Indicate the loans for the employee. Will be considered on the '
             'payslips.')

    number_fonacot = fields.Char(string="Number FONACOT",
        tracking=True, index=True,
        help='If comes from Fonacot, indicate the number.')

class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Allow register the loans in each employee (Fonacot)'

    name = fields.Char(
        'Number', help='Number for this record, if comes from Fonacot, use '
        '"No. Credito"', required=True, index=True)
    monthly_withhold = fields.Float(
        help='Indicates the amount to withhold in a monthly basis.')
    payment_term = fields.Integer(
        help='Indicates the payment term for this loan.')
    # loan_type = fields.Selection([
    #     ('company', 'Company'),
    #     ('fonacot', 'Fonacot'),
    # ], 'Type', help='Indicates the loan type.')
    loan_type_id = fields.Many2one('l10n.mx.loan.type', string='Type')
    contract_id = fields.Many2one(
        'hr.contract', help='Employee for this loan')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    company_currency_id = fields.Many2one('res.currency',
                                          related='contract_id.company_id.currency_id',
                                          string="Company Currency",
                                          compute_sudo=True,
                                          readonly=True)
    credit_amount = fields.Monetary(string="Credit Amount", currency_field='company_currency_id')
    payments_other_employers = fields.Monetary(string="Payments by other employers",
                                               currency_field='company_currency_id')
    accumulated_amount_withheld = fields.Monetary(string="Accumulated amount withheld",
                                                  currency_field='company_currency_id',
                                                  compute='_compute_accumulated_amount_withheld',
                                                  compute_sudo=True)
    count_payslip = fields.Integer(compute='_compute_accumulated_amount_withheld', compute_sudo=True)
    residue = fields.Monetary(string="Residue",
                              currency_field='company_currency_id',
                              compute='_compute_residue',
                              compute_sudo=True)
    employee_id = fields.Many2one('hr.employee', related='contract_id.employee_id', compute_sudo=True)
    amount_total = fields.Monetary(string='Total',
                                   currency_field='company_currency_id',
                                   compute='_compute_amount_total',
                                   compute_sudo=True)
    rule_id = fields.Many2one('hr.salary.rule', string='Rule')
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')

    @api.depends('credit_amount', 'payments_other_employers', 'accumulated_amount_withheld')
    def _compute_residue(self):
        for record in self:
            payments_other_employers = record.payments_other_employers \
                if record.payments_other_employers else 0
            record.residue = record.credit_amount - abs(payments_other_employers) - abs(record.accumulated_amount_withheld)

    @api.depends('contract_id', 'date_start', 'date_end', 'rule_id')
    def _compute_accumulated_amount_withheld(self):
        for record in self:
            domain = [('contract_id', '=', record.contract_id._origin.id),
                      ('date_from', '>=', record.date_start),
                      ('date_to', '<=', record.date_end),
                      ]
            payslips = self.env['hr.payslip'].search(domain)
            record.count_payslip = len(payslips)
            record.accumulated_amount_withheld = sum(payslips.line_ids.filtered(lambda l: l.salary_rule_id.id == record.rule_id.id).mapped('total'))

    @api.depends('credit_amount', 'monthly_withhold', 'payments_other_employers', 'accumulated_amount_withheld', 'residue')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = record.credit_amount + record.monthly_withhold + record.payments_other_employers +record.accumulated_amount_withheld + record.residue

