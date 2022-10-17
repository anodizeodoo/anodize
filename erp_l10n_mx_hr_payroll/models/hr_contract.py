# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    l10n_mx_payroll_holidays = fields.Integer(
        string="Days of holidays", default=6, tracking=True,
        help="Initial number of days for holidays. The minimum is 6 days.")
    l10n_mx_payroll_vacation_bonus = fields.Integer(
        string="Vacation bonus (%)", default=25, tracking=True,
        help="Percentage of vacation bonus. The minimum is 25 %.")
    l10n_mx_payroll_christmas_bonus = fields.Integer(
        string="Christmas bonus (days)", default=15, help="Number of day for "
        "the Christmas bonus. The minimum is 15 days' pay",
        tracking=True)
    l10n_mx_payroll_integrated_salary = fields.Float(
        'Integrated Salary', tracking=True,
        help='Used in the CFDI to express the salary '
        'that is integrated with the payments made in cash by daily quota, '
        'gratuities, perceptions, room, premiums, commissions, benefits in '
        'kind and any other quantity or benefit that is delivered to the '
        'worker by his work, Pursuant to Article 84 of the Federal Labor '
        'Law. (Used to calculate compensation).')
    l10n_mx_payroll_sdi_variable = fields.Float(
        'Variable SDI', default=0, tracking=True,
        help='Used when the salary type is mixed or variable. This value is '
        'integrated by the sum of perceptions in the previous two months and '
        'divided by the number of days worked. Also, it affects the '
        'integrated salary value.')
    l10n_mx_payrool_sdi_total = fields.Float(compute='_compute_payroll_total', string='SDI total',
                                         help='Get the sum of Variable SDI + Integrated Salary')
    # Overwrite options & default
    l10n_mx_payroll_schedule_pay = fields.Selection([
        ('01', 'Daily'),
        ('02', 'Weekly'),
        ('03', 'Biweekly'),
        ('04', 'Fortnightly'),
        ('05', 'Monthly'),
        ('06', 'Bimonthly'),
        ('07', 'Unit work'),
        ('08', 'Commission'),
        ('09', 'Raised price'),
        ('10', 'Decennial'),
        ('99', 'Other')], default='02', string=' Schedule Pay')

    l10n_mx_payroll_contract_type = fields.Selection([
        ('01', 'Contrato de trabajo por tiempo indeterminado'),
        ('02', 'Contrato de trabajo para obra determinada'),
        ('03', 'Contrato de trabajo por tiempo determinado'),
        ('04', 'Contrato de trabajo por temporada'),
        ('05', 'Contrato de trabajo sujeto a prueba'),
        ('06', 'Contrato de trabajo con capacitación inicial'),
        ('07', 'Modalidad de contratación por pago de hora laborada'),
        ('08', 'Modalidad de trabajo por comisión laboral'),
        ('09', 'Modalidades de contratación donde no existe relación de '
         'trabajo'),
        ('10', 'Jubilación, pensión, retiro'),
        ('99', 'Otro contrato')], string='Contract Type')

    l10n_mx_payroll_infonavit_type = fields.Selection(
        [('percentage', _('Percentage')),
         ('vsm', _('Number of minimum wages')),
         ('fixed_amount', _('Fixed amount')), ],
        string='INFONAVIT discount', help="INFONAVIT discount type that "
        "is calculated in the employee's payslip")
    l10n_mx_payroll_infonavit_rate = fields.Float(
        string='Infonavit rate', help="Value to be deducted in the employee's"
        " payment for the INFONAVIT concept.This depends on the INFONAVIT "
        "discount type as follows: \n- If the type is percentage, then the "
        "value of this field can be 1 - 100 \n- If the type is number of "
        "minimum wages, the value of this field may be 1 - 25, since it is "
        "\n- If the type is a fixed story, the value of this field must be "
        "greater than zero. In addition, the amount of this deduction must "
        "correspond to the payment period.")
    l10n_mx_payroll_food_voucher = fields.Float(
        'Food Voucher Amount',
        help='Amount to be paid in food voucher each payment period.')
    l10n_mx_payroll_punctuality_bonus = fields.Float(
        'Punctuality bonus', tracking=True,
        help='If the company offers punctuality bonus, indicate the bonus amount by payment period.')
    l10n_mx_payroll_attendance_bonus = fields.Float(
        'Attendance bonus', tracking=True,
        help='If the company offers attendance bonus, indicate the bonus amount by payment period.')

    @api.depends()
    def _compute_payroll_total(self):
        for record in self:
            record.l10n_mx_payrool_sdi_total = record.l10n_mx_payroll_integrated_salary + record.l10n_mx_payroll_sdi_variable

    def compute_payroll_integrated_salary(self):
        """Compute Daily Salary Integrated according to Mexican laws"""
        # the integrated salary cannot be more than 25 UMAs
        max_sdi = self.company_id.l10n_mx_payroll_uma * 25
        for record in self:
            sdi = record._get_payroll_static_SDI() + (
                record.l10n_mx_payroll_sdi_variable or 0)
            # the integrated salary cannot be less than 1 minimum wages
            sdi = self.company_id.l10n_mx_payroll_minimum_wage if (
                sdi < self.company_id.l10n_mx_payroll_minimum_wage) else sdi
            sdi = sdi if sdi < max_sdi else max_sdi
            record.l10n_mx_payroll_integrated_salary = sdi

    def compute_payroll_integrated_salary_variable(self):
        """Compute Daily Salary Integrated Variable according to Mexican laws"""
        payslips = self.env['hr.payslip']
        categories = self.env.ref(
            'erp_l10n_mx_hr_payroll.hr_payroll_salary_rule_category_perception_mx_taxed')
        categories |= self.env.ref(
            'erp_l10n_mx_hr_payroll.hr_payroll_salary_rule_category_perception_mx_exempt')
        date_mx = fields.datetime.now()
        date_from = (date_mx - timedelta(days=30 * (2 if date_mx.month % 2 else 3))).replace(day=1)
        date_to = (date_mx - timedelta(days=30 * (1 if date_mx.month % 2 else 2)))
        date_to = date_to.replace(day=calendar.monthrange(date_to.year, date_to.month)[1])
        for record in self:
            payslips = payslips.search([
                ('contract_id', '=', record.id), ('state', '=', 'done'),
                ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
            worked = sum(payslips.mapped('worked_days_line_ids').filtered(
                lambda work: work.code == 'WORK100').mapped('number_of_days'))
            inputs = sum(payslips.mapped('line_ids').filtered(
                lambda input: input.category_id in categories and not (input.code.endswith(
                    '001') or input.code.endswith('046'))).mapped('total'))
            record.l10n_mx_payroll_sdi_variable = (inputs / worked) if worked else 0

    def update_integrated_salary_variable(self):
        self.env['hr.contract'].search([
            ('state', '=', 'open'),
        ]).compute_payroll_integrated_salary_variable()

    def _get_payroll_static_SDI(self):
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
        vacation_bonus = (self.l10n_mx_payroll_vacation_bonus or 25) / 100
        holidays = self.get_current_holidays() * vacation_bonus
        bonus = self.l10n_mx_payroll_christmas_bonus or 15
        return 1 + (holidays + bonus)/365

    def get_current_holidays(self):
        """return number of days according with the seniority and holidays"""
        self.ensure_one()
        holidays = self.l10n_mx_payroll_holidays or 6
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

    @staticmethod
    def _l10n_mx_payroll_get_days(date_start, date_end):
        """Given two dates return the days elapsed between both dates"""
        date_start = fields.Date.from_string(date_start)
        date = fields.Date.from_string(date_end)
        days_work = ((date - date_start).days - 1)
        return 0 if days_work < 0 else days_work

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


class L10nMxEdiJobRank(models.Model):
    _name = "l10n_mx_edi.job.risk"
    _description = "Used to define the percent of each job risk."

    name = fields.Char(help='Job risk provided by the SAT.')
    code = fields.Char(help='Code assigned by the SAT for this job risk.')
    percentage = fields.Float(help='Percentage for this risk, is used in the '
                              'payroll rules.', digits=(2, 6),)


class PayrollHrEmployeeLoan(models.Model):
    _name = 'payroll.hr.employee.loan'
    _description = 'Allow register the loans in each employee (Fonacot)'

    name = fields.Char(
        'Number', help='Number for this record, if comes from Fonacot, use '
        '"No. Credito"', required=True)
    payroll_monthly_withhold = fields.Float(
        help='Indicates the amount to withhold in a monthly basis.')
    payroll_payment_term = fields.Integer(
        help='Indicates the payment term for this loan.')
    payslip_ids = fields.Many2many(
        'hr.payslip', help='Payslips where this loan is collected.')
    payroll_payslips_count = fields.Integer(
        'Number of Payslips', compute='_compute_payroll_payslips_count')
    payroll_loan_type = fields.Selection([
        ('company', 'Company'),
        ('fonacot', 'Fonacot'),
    ], 'Type', help='Indicates the loan type.')
    employee_id = fields.Many2one(
        'hr.employee', help='Employee for this loan')
    payroll_number_fonacot = fields.Char(
        help='If comes from Fonacot, indicate the number.')
    active = fields.Boolean(
        help='If the loan was paid the record will be deactivated.',
        default=True)

    def _compute_payroll_payslips_count(self):
        for loan in self:
            loan.payroll_payslips_count = len(loan.payslip_ids.filtered(
                lambda rec: rec.state == 'done'))

    def action_get_payslips_view(self):
        return {
            'name': _('Loan Payslips'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payslip_ids.filtered(
                lambda rec: rec.state == 'done').ids)],
        }


class L10nMxPayrollEmployerRegistration(models.Model):
    _name = 'l10n_mx_payroll.employer.registration'
    _description = 'Allow define all the employer registration from the company'
    _inherit = ['mail.thread']

    name = fields.Char(
        help='Value to set in the "RegistroPatronal" attribute.')
    payroll_job_risk_id = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', required=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # == External Trade ==
    l10n_mx_edi_curp = fields.Char(
        string="CURP", size=18,
        help="In Mexico, the Single Code of Population Registration (CURP) is a unique alphanumeric code of 18 "
             "characters used to officially identify both residents and Mexican citizens throughout the country.")

