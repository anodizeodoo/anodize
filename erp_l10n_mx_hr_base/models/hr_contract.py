# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'


    l10n_mx_payroll_integrated_salary = fields.Float(
        'Integrated Salary',
        compute='_compute_l10n_mx_payroll_integrated_salary',
        inverse='_inverse_l10n_mx_payroll_integrated_salary',
        readonly=False,
        help='Used in the CFDI to express the salary '
        'that is integrated with the payments made in cash by daily quota, '
        'gratuities, perceptions, room, premiums, commissions, benefits in '
        'kind and any other quantity or benefit that is delivered to the '
        'worker by his work, Pursuant to Article 84 of the Federal Labor '
        'Law. (Used to calculate compensation).')
    l10n_mx_payroll_integrated_salary_manual = fields.Float(
        'Integrated Salary',
        tracking=True)
    l10n_mx_payroll_daily_salary = fields.Float(
        'Daily Salary',
        compute='_compute_l10n_mx_payroll_daily_salary',
        inverse='_inverse_l10n_mx_payroll_daily_salary')
    l10n_mx_payroll_daily_salary_manual = fields.Float(
        'Daily Salary',
        tracking=True)
    l10n_mx_payroll_sdi_variable = fields.Float(
        'Variable SDI',
        default=0,
        tracking=True,
        help='Used when the salary type is mixed or variable. This value is '
        'integrated by the sum of perceptions in the previous two months and '
        'divided by the number of days worked. Also, it affects the '
        'integrated salary value.')

    # Overwrite options & default
    l10n_mx_payroll_schedule_pay_id = fields.Many2one('l10n.mx.payroll.schedule.pay',
                                                      tracking=True,
                                                      string='Schedule Pay')

    l10n_mx_payroll_contract_type_id = fields.Many2one('l10n.mx.payroll.contract.type',
                                                       tracking=True,
                                                       string='Contract type')
    l10n_mx_type_benefit_id = fields.Many2one('l10n.mx.type.benefit',
                                              tracking=True,
                                              string='Types of Benefits')

    l10n_mx_payroll_food_voucher = fields.Float(
        'Food Voucher Amount',
        tracking=True,
        help='Amount to be paid in food voucher each payment period.')
    l10n_mx_payroll_punctuality_bonus = fields.Float(
        'Punctuality bonus',
        tracking=True,
        help='If the company offers punctuality bonus, indicate the bonus amount by payment period.')
    l10n_mx_payroll_attendance_bonus = fields.Float(
        'Attendance bonus',
        tracking=True,
        help='If the company offers attendance bonus, indicate the bonus amount by payment period.')
    l10n_mx_payroll_gasoline_voucher = fields.Float('Gasoline Vouchers', tracking=True)
    l10n_mx_payroll_restaurant_voucher = fields.Float('Restaurant Vouchers', tracking=True)
    l10n_mx_payroll_school_support_bonus = fields.Float('School support', tracking=True)
    l10n_mx_payroll_transportation_bonus = fields.Float('Transportation', tracking=True)
    l10n_mx_payroll_funeral_expenses_bonus = fields.Float('Funeral expenses', tracking=True)

    l10n_mx_payroll_infonavit_type = fields.Selection(
        [('percentage', _('Percentage')),
         ('vsm', _('Number of minimum wages')),
         ('fixed_amount', _('Fixed amount')), ],
        tracking=True,
        string='INFONAVIT discount', help="INFONAVIT discount type that "
                                          "is calculated in the employee's payslip")
    l10n_mx_payroll_infonavit_rate = fields.Float(
        string='Infonavit rate',
        tracking=True,
        help="Value to be deducted in the employee's"
                                      " payment for the INFONAVIT concept.This depends on the INFONAVIT "
                                      "discount type as follows: \n- If the type is percentage, then the "
                                      "value of this field can be 1 - 100 \n- If the type is number of "
                                      "minimum wages, the value of this field may be 1 - 25, since it is "
                                      "\n- If the type is a fixed story, the value of this field must be "
                                      "greater than zero. In addition, the amount of this deduction must "
                                      "correspond to the payment period.")
    l10n_mx_payroll_infonavit_credit_number = fields.Integer(string='Credit number', tracking=True)
    l10n_mx_payroll_infonavit_active = fields.Boolean(string='Infonavit Active', tracking=True)
    l10n_mx_payroll_infonavit_description = fields.Char(string='Description', tracking=True)
    l10n_mx_payroll_infonavit_date_start = fields.Date(string='Date Start Aplication', tracking=True)
    l10n_mx_payroll_infonavit_date_register = fields.Date(string='Date Register', tracking=True)

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

    def _get_days_in_current_period(self, date_to=False, start_year=False):
        """Get days at current period to compute payments' proportional part

        :param date_to: date to get the days
        :type date_to: str
        :param start_year: period start at 1 Jan
        :type start_year: boolean
        :return: number of days of the contract in current period
        :rtype: int
        """
        date = date_to or fields.Date.today()
        contract_date = self.date_start
        if start_year:
            date_start = fields.date(date.year, 1, 1)
            if (contract_date - date_start).days > 0:
                date_start = contract_date
            return (date - date_start).days + 1
        date_start = fields.date(
            contract_date.year, contract_date.month, contract_date.day)
        if (date - date_start).days < 0:
            date_start = fields.date(
                date.year - 1, contract_date.month, contract_date.day)
        return (date - date_start).days + 1

    @api.depends('wage', 'l10n_mx_type_benefit_id.day_month',
                 'l10n_mx_payroll_daily_salary_manual')
    def _compute_l10n_mx_payroll_daily_salary(self):
        for record in self:
            if record.l10n_mx_payroll_daily_salary_manual:
                record.l10n_mx_payroll_daily_salary = record.l10n_mx_payroll_daily_salary_manual
            else:
                if record.wage and record.l10n_mx_type_benefit_id.day_month:
                    record.l10n_mx_payroll_daily_salary = record.wage / record.l10n_mx_type_benefit_id.day_month
                else:
                    record.l10n_mx_payroll_daily_salary = False

    def _inverse_l10n_mx_payroll_daily_salary(self):
        for record in self:
            record.l10n_mx_payroll_daily_salary_manual = record.l10n_mx_payroll_daily_salary

    @api.onchange('wage')
    def _onchange_wage_mx(self):
        self.l10n_mx_payroll_integrated_salary_manual = 0.0
        self.l10n_mx_payroll_daily_salary_manual = 0.0

    @api.onchange('l10n_mx_type_benefit_id', 'date_start', 'l10n_mx_payroll_daily_salary')
    def _onchange_l10n_mx_type_benefit_id(self):
        if self.l10n_mx_type_benefit_id and self.date_start:
            antiquity = relativedelta(fields.Date.today(), self.date_start).years
            type_benefit_line_id = self.l10n_mx_type_benefit_id.find_rule_by_antiquity(antiquity)
            self.l10n_mx_holidays = type_benefit_line_id.holidays
            self.l10n_mx_payroll_integrated_salary = self.l10n_mx_payroll_daily_salary * type_benefit_line_id.integration_factor

    @api.depends('l10n_mx_type_benefit_id', 'l10n_mx_payroll_daily_salary',
                 'date_start', 'l10n_mx_payroll_integrated_salary_manual')
    def _compute_l10n_mx_payroll_integrated_salary(self):
        for record in self:
            if record.l10n_mx_payroll_integrated_salary_manual:
                record.l10n_mx_payroll_integrated_salary = record.l10n_mx_payroll_integrated_salary_manual
            else:
                precision_digits = self.env['decimal.precision'].precision_get(record.sudo().currency_id.name)
                if record.l10n_mx_type_benefit_id and record.l10n_mx_payroll_daily_salary and record.date_start:
                    antiquity = relativedelta(fields.Date.today(), record.date_start).years
                    type_benefit_line_id = record.l10n_mx_type_benefit_id.find_rule_by_antiquity(antiquity)
                    l10n_mx_payroll_integrated_salary = record.l10n_mx_payroll_daily_salary \
                                                        * type_benefit_line_id.integration_factor
                    record.l10n_mx_payroll_integrated_salary = float('%0.*f' % (precision_digits,
                                                                                l10n_mx_payroll_integrated_salary))
                else:
                    record.l10n_mx_payroll_integrated_salary = False

    def _inverse_l10n_mx_payroll_integrated_salary(self):
        for record in self:
            record.l10n_mx_payroll_integrated_salary_manual = record.l10n_mx_payroll_integrated_salary