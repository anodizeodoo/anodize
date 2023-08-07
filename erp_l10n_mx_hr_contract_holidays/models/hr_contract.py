# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
import threading
import datetime
from datetime import date
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    def _default_l10n_mx_number(self):
        sequence_id = self.env['ir.sequence'].search([('code', '=', 'hr.contract.number')])
        if sequence_id:
            return sequence_id.get_next_char(sequence_id.number_next_actual)
        return False

    l10n_mx_holidays = fields.Integer(
        string="Days of holidays",
        default=6,
        tracking=True,
        index=True,
        help="Initial number of days for holidays. The minimum is 6 days.")

    l10n_mx_vacation_bonus = fields.Integer(
        string="Vacation cousin (%)",
        tracking=True,
        # compute='_compute_l10n_mx_vacation_christmas_bonus',
        compute_sudo=True,
        help="Percentage of vacation bonus. The minimum is 25 %.")
    l10n_mx_christmas_bonus = fields.Integer(
        string="Bonus Days", help="Number of day for "
                                                          "the Christmas bonus. The minimum is 15 days' pay",
        # compute='_compute_l10n_mx_vacation_christmas_bonus',
        tracking=True,
        compute_sudo=True)
    l10n_mx_antiquity = fields.Char('Antiquity', compute="_compute_l10n_mx_antiquity")
    l10n_mx_antiquity_days = fields.Char('Días', compute="_compute_l10n_mx_antiquity_days")
    l10n_mx_antiquity_other = fields.Char('Antiguedad Fecha Inicio', compute="_compute_l10n_mx_antiquity_other")
    l10n_mx_antiquity_other_days = fields.Char('Días', compute="_compute_l10n_mx_antiquity_other_days")

    l10n_mx_number = fields.Char(default=lambda self: self._default_l10n_mx_number(),
                                 string='No. Contract', tracking=True, index=True)
    l10n_mx_automatic_sequence_contracts = fields.Boolean(related='company_id.l10n_mx_automatic_sequence_contracts',
                                                          compute_sudo=True)
    name = fields.Char(required=False, tracking=True, index=True)

    l10n_mx_date_imss = fields.Date(string='IMSS discharge date')
    state = fields.Selection(selection_add=[('renovate', 'To Renovate')])
    date_end_period = fields.Date(string='End Date of the Trial Period')
    hourly_wage = fields.Float(string='Hourly wage', compute='_compute_hourly_wage', readonly=False)
    contract_holidays_ids = fields.One2many('hr.contract.holidays', 'holidays_contract_id', 'Holidays')

    work_days = fields.Float(string='Work Days', compute='_compute_work_days')
    total_disabilities = fields.Integer(string='Total Disabilities', compute='_compute_total_disabilities')
    total_unexcused_absences = fields.Integer(string='Total Unexcused Absences', compute='_compute_total_unexcused_absences')
    total_discounted_days_ptu = fields.Integer(string='Total Discounted Days PTU', compute='_compute_total_discounted_days_ptu')

    @api.depends('l10n_mx_payroll_daily_salary', 'resource_calendar_id.hours_per_day')
    def _compute_hourly_wage(self):
        for record in self:
            record.hourly_wage = record.l10n_mx_payroll_daily_salary / record.resource_calendar_id.hours_per_day

    def get_work_days_domains(self, date_from, date_to):
        domain_wd = [('employee_id', '=', self.sudo().employee_id.id),
                  ('date_from', '>=', date_from),
                  ('date_to', '<=', date_to)]

        return domain_wd

    def _compute_work_days(self):
        date_from = datetime.date(month=1, year=datetime.datetime.now().year, day=1)
        date_to = datetime.date(month=12, year=datetime.datetime.now().year, day=31)
        domain = self.get_work_days_domains(date_from, date_to)
        worked_days_line = self.env['hr.payslip'].search(domain).worked_days_line_ids.filtered(lambda l: l.work_entry_type_id.code == 'WORK100')
        self.work_days = sum(line.number_of_days for line in worked_days_line)

    def _compute_total_disabilities(self):
        date_from = datetime.date(month=1, year=datetime.datetime.now().year, day=1)
        date_to = datetime.date(month=12, year=datetime.datetime.now().year, day=31)
        domain = [('employee_id', '=', self.employee_id.id),
                  ('date_from', '>=', date_from),
                  ('date_to', '<=', date_to),
                  ('type', '=', 'disabilities')]
        self.total_disabilities = sum(line.number_of_days for line in self.env['hr.leave'].search(domain))

    def _compute_total_unexcused_absences(self):
        date_from = datetime.date(month=1, year=datetime.datetime.now().year, day=1)
        date_to = datetime.date(month=12, year=datetime.datetime.now().year, day=31)
        domain = [('employee_id', '=', self.employee_id.id),
                  ('date_from', '>=', date_from),
                  ('date_to', '<=', date_to),
                  ('holiday_status_id', '=', self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_08').id)]
        self.total_unexcused_absences = sum(line.number_of_days for line in self.env['hr.leave'].search(domain))

    @api.depends('total_disabilities', 'total_unexcused_absences')
    def _compute_total_discounted_days_ptu(self):
        self.total_discounted_days_ptu = self.total_disabilities + self.total_unexcused_absences

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

    @api.depends('date_start')
    def _compute_l10n_mx_antiquity(self):
        for record in self:
            if record.date_start:
                years = relativedelta(fields.Date.today(), record.date_start).years
                months = relativedelta(fields.Date.today(), record.date_start).months
                days = relativedelta(fields.Date.today(), record.date_start).days
                record.l10n_mx_antiquity = _('{} Year(s) {} Month(s) {} Day(s)').format(years, months, days)
            else:
                record.l10n_mx_antiquity = False

    @api.depends('date_start')
    def _compute_l10n_mx_antiquity_days(self):
        for record in self:
            if record.date_start:
                years = relativedelta(fields.Date.today(), record.date_start).years
                months = relativedelta(fields.Date.today(), record.date_start).months
                days = relativedelta(fields.Date.today(), record.date_start).days
                record.l10n_mx_antiquity_days = (years * 365) + (months * 30) + days
            else:
                record.l10n_mx_antiquity_days = False

    @api.depends('l10n_mx_date_imss')
    def _compute_l10n_mx_antiquity_other(self):
        for record in self:
            if record.l10n_mx_date_imss:
                years1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).years
                months1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).months
                days1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).days
                record.l10n_mx_antiquity_other = _('{} Year(s) {} Month(s) {} Day(s)').format(years1, months1, days1)
            else:
                record.l10n_mx_antiquity_other = False

    @api.depends('l10n_mx_date_imss')
    def _compute_l10n_mx_antiquity_other_days(self):
        for record in self:
            if record.l10n_mx_date_imss:
                years1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).years
                months1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).months
                days1 = relativedelta(fields.Date.today(), record.l10n_mx_date_imss).days
                record.l10n_mx_antiquity_other_days = (years1 * 365) + (months1 * 30) + days1
            else:
                record.l10n_mx_antiquity_other_days = False

    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        if res.l10n_mx_automatic_sequence_contracts:
            sequence_id = self.env.user.company_id.contract_id_sequence
            if sequence_id:
                code = sequence_id.code
                mx_number = self.env["ir.sequence"].next_by_code(code)
                # vals["l10n_mx_number"] = mx_number
                # vals["name"] = mx_number
                res.l10n_mx_number = mx_number
                res.name = mx_number
        res.state = 'open'
        return res

    def write(self, vals):
        result = super(HrContract, self).write(vals)
        if self.state == 'draft':
            self.state = 'open'
        return result

    def button_new(self):
        self.write({'state': 'draft'})

    def button_cancel(self):
        self.write({'state': 'cancel'})

    def button_modify_date_imss(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Modify Date IMSS'),
            'res_model': 'modify.date.imss.wizard',
            'view_mode': 'form',
            'target': 'new'
        }

    def button_close(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Modify State Contract'),
            'res_model': 'modify.state.contract.wizard',
            'view_mode': 'form',
            'target': 'new'
        }

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
            self.l10n_mx_vacation_bonus = type_benefit_line_id.vacation_cousin
            self.l10n_mx_christmas_bonus = type_benefit_line_id.bonus_days
        else:
            self.l10n_mx_vacation_bonus = False
            self.l10n_mx_christmas_bonus = False

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

    @api.model
    def update_state(self):
        # super(HrContract, self).update_state()
        from_cron = 'from_cron' in self.env.context
        contracts = self.search([
            ('state', '=', 'open'), ('kanban_state', '!=', 'blocked'),
            '|',
            '&',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=7))),
            ('date_end', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
            '&',
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=60))),
            ('visa_expire', '>=', fields.Date.to_string(date.today() + relativedelta(days=1))),
        ])

        for contract in contracts:
            contract.activity_schedule(
                'mail.mail_activity_data_todo', contract.date_end,
                _("The contract of %s is about to expire.", contract.employee_id.name),
                user_id=contract.hr_responsible_id.id or self.env.uid)

        if contracts:
            contracts._safe_write_for_cron({'kanban_state': 'blocked'}, from_cron)

        days = self.company_id.number_days_contracts
        contracts_to_close = self.search([
            ('state', '=', 'open'),
            '|',
            ('date_end', '<=', fields.Date.to_string(date.today() + relativedelta(days=days))),
            ('visa_expire', '<=', fields.Date.to_string(date.today() + relativedelta(days=days))),
        ])

        if contracts_to_close:
            contracts_to_close._safe_write_for_cron({'state': 'renovate'}, from_cron)

        contracts_to_open = self.search([('state', '=', 'draft'), ('kanban_state', '=', 'done'),
                                         ('date_start', '<=', fields.Date.to_string(date.today())), ])

        if contracts_to_open:
            contracts_to_open._safe_write_for_cron({'state': 'open'}, from_cron)

        contract_ids = self.search([('date_end', '=', False), ('state', '=', 'close'), ('employee_id', '!=', False)])
        # Ensure all closed contract followed by a new contract have a end date.
        # If closed contract has no closed date, the work entries will be generated for an unlimited period.
        for contract in contract_ids:
            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('state', 'not in', ['cancel', 'new']),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)
            if next_contract:
                contract._safe_write_for_cron({'date_end': next_contract.date_start - relativedelta(days=1)}, from_cron)
                continue
            next_contract = self.search([
                ('employee_id', '=', contract.employee_id.id),
                ('date_start', '>', contract.date_start)
            ], order="date_start asc", limit=1)
            if next_contract:
                contract._safe_write_for_cron({'date_end': next_contract.date_start - relativedelta(days=1)}, from_cron)

        return True

    def _safe_write_for_cron(self, vals, from_cron=False):
        if from_cron:
            auto_commit = not getattr(threading.current_thread(), 'testing', False)
            for contract in self:
                try:
                    with self.env.cr.savepoint():
                        contract.write(vals)
                except ValidationError as e:
                    _logger.warning(e)
                else:
                    if auto_commit:
                        self.env.cr.commit()
        else:
            self.write(vals)


class HrContractHolidays(models.Model):
    _name = "hr.contract.holidays"
    _description = 'Holidays'

    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    holiday_status_id = fields.Many2one('hr.leave.type', string='Absence Type')
    days_assigned = fields.Float(string='Days Assigned')
    days_enjoyed = fields.Float(string='Days Enjoyed')
    days_available = fields.Float(string='Days Available')
    hr_leave_id = fields.Many2one('hr.leave', string='Holidays')
    holidays_contract_id = fields.Many2one('hr.contract', string='Contract')
    state = fields.Selection(related='hr_leave_id.state', compute_sudo=True)