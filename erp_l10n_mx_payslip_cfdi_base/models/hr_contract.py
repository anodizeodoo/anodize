# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    l10n_mx_sdi_total = fields.Float(compute='_compute_sdi_total', string='SDI total',
                                         tracking=True,
                                         help='Get the sum of Variable SDI + Integrated Salary')

    @api.depends()
    def _compute_sdi_total(self):
        for record in self:
            record.l10n_mx_sdi_total = record.l10n_mx_payroll_integrated_salary + record.l10n_mx_payroll_sdi_variable

    def compute_integrated_salary(self):
        """Compute Daily Salary Integrated according to Mexican laws"""
        # the integrated salary cannot be more than 25 UMAs
        max_sdi = self.company_id.l10n_mx_uma * 25
        for record in self:
            sdi = record._get_static_SDI() + (
                record.l10n_mx_payroll_sdi_variable or 0)
            # the integrated salary cannot be less than 1 minimum wages
            sdi = self.company_id.l10n_mx_minimum_wage if (
                sdi < self.company_id.l10n_mx_minimum_wage) else sdi
            sdi = sdi if sdi < max_sdi else max_sdi
            record.l10n_mx_payroll_integrated_salary = sdi

    def _get_static_SDI(self):
        """Get the integrated salary for the static perceptions like:
            - Salary
            - holidays
            - Christmas bonus
        """
        self.ensure_one()
        return self.wage / 30 * self._get_integration_factor()

    def _get_integration_factor(self):
        """get the factor used to get the static integrated salary
        overwrite to add new static perceptions.
        factor = 1 + static perceptions/365
        new_factor = factor + new_perception / 365
        """
        self.ensure_one()
        vacation_bonus = (self.l10n_mx_vacation_bonus or 25) / 100
        holidays = self.get_current_holidays() * vacation_bonus
        bonus = self.l10n_mx_christmas_bonus or 15
        return 1 + (holidays + bonus)/365