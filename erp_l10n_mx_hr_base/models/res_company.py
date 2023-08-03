# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_edi_employer_registration_id = fields.Many2one('l10n_mx_payroll.employer.registration', 'Employer Registration')
    l10n_mx_daily_salary_calculation = fields.Selection(
        [('daily', 'Daily Salary Capture'), ('monthly', 'From the Monthly Salary')], string='Daily Salary Calculation',
        default='monthly')

