# coding: utf-8
import calendar
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_loan = fields.Boolean(string='Loan', default=False)
