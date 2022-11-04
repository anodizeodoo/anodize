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

class HrContract(models.Model):
    _inherit = "hr.contract"

    loan_ids = fields.One2many(
        'hr.employee.loan', 'contract_id', 'Loans', context={'active_test': False},
        help='Indicate the loans for the employee. Will be considered on the '
             'payslips.')
    work_fonacot = fields.Char(string="Workplace FONACOT")
    number_fonacot = fields.Char(string="Number FONACOT",
        help='If comes from Fonacot, indicate the number.')

class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Allow register the loans in each employee (Fonacot)'

    name = fields.Char(
        'Number', help='Number for this record, if comes from Fonacot, use '
        '"No. Credito"', required=True)
    monthly_withhold = fields.Float(
        help='Indicates the amount to withhold in a monthly basis.')
    payment_term = fields.Integer(
        help='Indicates the payment term for this loan.')
    loan_type = fields.Selection([
        ('company', 'Company'),
        ('fonacot', 'Fonacot'),
    ], 'Type', help='Indicates the loan type.')
    contract_id = fields.Many2one(
        'hr.contract', help='Employee for this loan')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True)
    date_start = fields.Date(string="Date Start")
    date_end = fields.Date(string="Date End")
    company_currency_id = fields.Many2one('res.currency', related='contract_id.company_id.currency_id', string="Company Currency",
                                          readonly=True)
    credit_amount = fields.Monetary(string="Credit Amount", currency_field='company_currency_id')
    payments_other_employers = fields.Monetary(string="Payments by other employers", currency_field='company_currency_id')
    accumulated_amount_withheld = fields.Monetary(string="Accumulated amount withheld", currency_field='company_currency_id',
                                                  compute='_compute_accumulated_amount_withheld')
    residue = fields.Monetary(string="Residue", currency_field='company_currency_id', compute='_compute_residue')

    @api.depends('credit_amount', 'payments_other_employers', 'accumulated_amount_withheld')
    def _compute_residue(self):
        for record in self:
            payments_other_employers = record.payments_other_employers if record.payments_other_employers else 0
            record.residue = record.credit_amount - payments_other_employers - record.accumulated_amount_withheld

    def _compute_accumulated_amount_withheld(self):
        for record in self:
            record.accumulated_amount_withheld = 100

