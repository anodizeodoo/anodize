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

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    loan_ids = fields.One2many(
        'hr.employee.loan', 'employee_id', 'Loans',
        help='Indicate the loans for the employee. Will be considered on the '
             'payslips.')

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
    employee_id = fields.Many2one(
        'hr.employee', help='Employee for this loan')
    number_fonacot = fields.Char(
        help='If comes from Fonacot, indicate the number.')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True)

