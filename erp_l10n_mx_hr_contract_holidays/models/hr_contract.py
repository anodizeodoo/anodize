# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _default_l10n_mx_number(self):
        sequence_id = self.env['ir.sequence'].search([('code', '=', 'hr.contract.number')])
        if sequence_id:
            return sequence_id.get_next_char(sequence_id.number_next_actual)
        return False

    l10n_mx_holidays = fields.Integer(
        string="Days of holidays", default=6, tracking=True,
        help="Initial number of days for holidays. The minimum is 6 days.")

    l10n_mx_vacation_bonus = fields.Integer(
        string="Vacation cousin (%)", tracking=True, compute='_compute_l10n_mx_vacation_christmas_bonus',
        help="Percentage of vacation bonus. The minimum is 25 %.")
    l10n_mx_christmas_bonus = fields.Integer(
        string="Bonus Days", help="Number of day for "
                                                          "the Christmas bonus. The minimum is 15 days' pay",
        compute='_compute_l10n_mx_vacation_christmas_bonus', tracking=True)
    l10n_mx_antiquity = fields.Char('Antiquity', compute="_compute_l10n_mx_antiquity")

    l10n_mx_number = fields.Char(default=lambda self: self._default_l10n_mx_number(), string='No. Contract')
    l10n_mx_automatic_sequence_contracts = fields.Boolean(related='company_id.l10n_mx_automatic_sequence_contracts')
    name = fields.Char(required=False)

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
        vacation_bonus = (self.l10n_mx_edi_vacation_bonus or 25) / 100
        holidays = self.get_current_holidays() * vacation_bonus
        bonus = self.l10n_mx_edi_christmas_bonus or 15
        return 1 + (holidays + bonus)/365

    def get_current_holidays(self):
        """return number of days according with the seniority and holidays"""
        self.ensure_one()
        holidays = self.l10n_mx_edi_holidays or 6
        seniority = self.get_seniority()['years']
        if seniority < 4:
            return holidays + 2 * (seniority)
        return holidays + 6 + 2 * floor((seniority + 1) / 5)

    def get_seniority(self, date_from=False, date_to=False, method='r'):
        """Return seniority between contract's date_start and date_to or today

        :param date_from: start date (default contract.date_start)
        :type date_from: str
        :param date_to: end date (default today)
        :type date_to: str
        :param method: {'r', 'a'} kind of values returned
        :type method: str
        :return: a dict with the values years, months, days.
            These values can be relative or absolute.
        :rtype: dict
        """
        self.ensure_one()
        datetime_start = date_from or self.date_start
        date = date_to or fields.Date.today()
        relative_seniority = relativedelta(date, datetime_start)
        if method == 'r':
            return {'years': relative_seniority.years,
                    'months': relative_seniority.months,
                    'days': relative_seniority.days}
        return {'years': relative_seniority.years,
                'months': (relative_seniority.months + relative_seniority
                           .years * 12),
                'days': (date - datetime_start).days + 1}


    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        if res.l10n_mx_automatic_sequence_contracts:
            number = self.env["ir.sequence"].next_by_code("hr.contract.number")
            res.l10n_mx_number = number
            res.name = number
        return res

    @api.depends('date_start')
    def _compute_l10n_mx_antiquity(self):
        for record in self:
            years = relativedelta(fields.Date.today(), record.date_start).years
            months = relativedelta(fields.Date.today(), record.date_start).months
            days = relativedelta(fields.Date.today(), record.date_start).days
            record.l10n_mx_antiquity = _('{} Year(s) {} Month(s) {} Day(s)').format(years, months, days)

    def action_update_l10n_mx_holidays(self):
        # table_holidays_obj = self.env['l10n.mx.table.holidays']
        # month = (relativedelta(fields.Date.today(), self.date_start).years * 12) + relativedelta(fields.Date.today(), self.date_start).months
        # tabulator_id = table_holidays_obj.find_rule_by_month(month)
        # self.l10n_mx_holidays = tabulator_id.l10n_mx_days
        if self.l10n_mx_type_benefit_id and self.date_start:
            antiquity = relativedelta(fields.Date.today(), self.date_start).years
            type_benefit_line_id = self.l10n_mx_type_benefit_id.find_rule_by_antiquity(antiquity)
            self.l10n_mx_holidays = type_benefit_line_id.holidays

    @api.depends('l10n_mx_type_benefit_id', 'date_start')
    def _compute_l10n_mx_vacation_christmas_bonus(self):
        for record in self:
            if record.l10n_mx_type_benefit_id and record.date_start:
                antiquity = relativedelta(fields.Date.today(), record.date_start).years
                type_benefit_line_id = record.l10n_mx_type_benefit_id.find_rule_by_antiquity(antiquity)
                record.l10n_mx_vacation_bonus = type_benefit_line_id.vacation_cousin
                record.l10n_mx_christmas_bonus = type_benefit_line_id.bonus_days
            else:
                record.l10n_mx_vacation_bonus = False
                record.l10n_mx_christmas_bonus = False
