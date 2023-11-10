# coding: utf-8
import calendar
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_finiquito = fields.Boolean(string='Finiquito', default=False)


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    is_finiquito = fields.Boolean(string='Finiquito', default=False)