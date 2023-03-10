# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta


class ModifySalary(models.Model):
    _name = "l10n.mx.modify.salary"
    _description = "Modify Salary"
    _rec_name = 'increment_type_id'

    application_date = fields.Date(string='Application Date')
    increment_type_id = fields.Many2one('l10n.mx.increment.type', 'Increment type')
    salary_employee_ids = fields.One2many('l10n.mx.salary.employee', 'modify_salary_id', 'Salary by Employee')

    @api.model
    def default_get(self, fields):
        res = super(ModifySalary, self).default_get(fields)
        contract_ids = self.env['hr.contract'].search([('state', '=', 'open')])
        salary_employee_obj = self.env['l10n.mx.salary.employee']
        salary_employee = []
        for contract in contract_ids:
            years = relativedelta(datetime.now().date(), contract.date_start).years + 1
            type_benefit_line_id = contract.l10n_mx_type_benefit_id.find_rule_by_antiquity(years)
            salary_employee_id = salary_employee_obj.create({
                'contract_id': contract.id,
                'employee_id': contract.employee_id.id,
                'job_id': contract.job_id.id,
                'department_id': contract.department_id.id,
                'integration_factor': type_benefit_line_id.integration_factor,
                'l10n_mx_payroll_daily_salary': contract.l10n_mx_payroll_daily_salary,
                'l10n_mx_payroll_integrated_salary': contract.l10n_mx_payroll_integrated_salary,

            })
            salary_employee.append(salary_employee_id.id)
        res['salary_employee_ids'] = [(6, 0, salary_employee)]
        return res

    def modify_salary(self):
        for line in self.salary_employee_ids:
            l10n_mx_payroll_daily_salary_new = line.l10n_mx_payroll_daily_salary_new if line.l10n_mx_payroll_daily_salary_new != 0 else line.l10n_mx_payroll_daily_salary
            l10n_mx_payroll_integrated_salary_new = line.l10n_mx_payroll_integrated_salary_new if line.l10n_mx_payroll_integrated_salary_new != 0 else line.l10n_mx_payroll_integrated_salary
            line.contract_id.write({
                'l10n_mx_payroll_daily_salary': l10n_mx_payroll_daily_salary_new,
                'l10n_mx_payroll_integrated_salary': l10n_mx_payroll_integrated_salary_new * line.integration_factor,
            })
        return True


class SalaryEmployee(models.Model):
    _name = 'l10n.mx.salary.employee'
    _description = "Salary Employee"

    modify_salary_id = fields.Many2one('l10n.mx.modify.salary', string='Modify salary')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    job_id = fields.Many2one('hr.job', string='Job')
    department_id = fields.Many2one('hr.department', string='Department')
    state = fields.Selection(related='contract_id.state')
    l10n_mx_payroll_daily_salary = fields.Float(string='Daily Salary')
    l10n_mx_payroll_integrated_salary = fields.Float(string='Integrated Salary')
    type_salary = fields.Selection(related='contract_id.type_salary')
    l10n_mx_date_imss = fields.Date(related='contract_id.l10n_mx_date_imss')
    l10n_mx_antiquity = fields.Integer('Antiquity', compute="_compute_l10n_mx_antiquity")
    l10n_mx_type_benefit_id = fields.Many2one(related='contract_id.l10n_mx_type_benefit_id')
    l10n_mx_holidays = fields.Integer(string="Days of holidays", compute='_compute_l10n_mx_contract_data')
    l10n_mx_vacation_bonus = fields.Integer(string="Vacation cousin (%)", compute='_compute_l10n_mx_contract_data')
    l10n_mx_christmas_bonus = fields.Integer(string="Bonus Days", compute='_compute_l10n_mx_contract_data')
    integration_factor = fields.Float(string='Integration Factor')
    l10n_mx_payroll_daily_salary_new = fields.Float(string='SD New', digits=(16, 2))
    l10n_mx_payroll_integrated_salary_new = fields.Float(string='SBC New', digits=(16, 2))

    @api.depends('contract_id')
    def _compute_l10n_mx_antiquity(self):
        for record in self:
            years = relativedelta(fields.Date.today(), record.contract_id.date_start).years + 1
            record.l10n_mx_antiquity = years

    @api.depends('l10n_mx_type_benefit_id', 'contract_id', 'l10n_mx_antiquity')
    def _compute_l10n_mx_contract_data(self):
        for record in self:
            if record.l10n_mx_type_benefit_id and record.l10n_mx_antiquity:
                type_benefit_line_id = record.l10n_mx_type_benefit_id.find_rule_by_antiquity(record.l10n_mx_antiquity)
                record.l10n_mx_holidays = type_benefit_line_id.holidays
                record.l10n_mx_vacation_bonus = type_benefit_line_id.vacation_cousin
                record.l10n_mx_christmas_bonus = type_benefit_line_id.bonus_days
            else:
                record.l10n_mx_holidays = False
                record.l10n_mx_vacation_bonus = False
                record.l10n_mx_christmas_bonus = False
