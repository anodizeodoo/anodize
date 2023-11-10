# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class EmployeePTU(models.Model):
    _name = "l10n.mx.employee.ptu"
    _description = "Employee PTU"

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year, datetime.now().year - 5, -1)]

    employee_id = fields.Many2one('hr.employee', string='Employee', index=True)
    registration_number = fields.Char(related='employee_id.registration_number',
                                      string='Code', compute_sudo=True)
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', index=True)
    type = fields.Selection([("S", "S"), ("C", "C")], string='Type', index=True)
    l10n_mx_payroll_contract_type_id = fields.Many2one('l10n.mx.payroll.contract.type', string='Contract type', index=True)
    number_of_days = fields.Float(string='Number of Days', index=True)
    salary_accrued = fields.Float(string='Salary Accrued', index=True)
    qty_days = fields.Float(string='Quantity Days', index=True)
    qty_amount = fields.Float(string='Quantity Amount', index=True)
    salary = fields.Float(string='Salary', index=True)
    salary3_month = fields.Float(string='Salary 3 Month', index=True)
    date_year = fields.Selection(selection=_get_years, string='Year', default=lambda s: str(datetime.today().year))
    date_from = fields.Date(string='Date from', compute='_compute_date')
    date_to = fields.Date(string='Date to', compute='_compute_date')

    @api.depends('date_year')
    def _compute_date(self):
        for record in self:
            if record.date_year:
                record.date_from = datetime(int(record.date_year), 1, 1)
                record.date_to = datetime(int(record.date_year), 12, 31)
            else:
                record.date_from = False
                record.date_to = False
