# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ModifySalary(models.Model):
    _name = "l10n.mx.modify.salary"
    _description = "Modify Salary"
    _rec_name = 'increment_type_id'

    application_date = fields.Date(string='Application Date')
    increment_type_id = fields.Many2one('l10n.mx.increment.type', 'Increment type', index=True)
    increase_amount = fields.Float(string='Increase amount', digits=(16, 2), index=True)
    increase_percent = fields.Float(string='Increase percent', digits=(16, 2), index=True)
    increase_salary = fields.Float(string='Increase salary', digits=(16, 2), index=True)
    label_increase = fields.Selection([
        ('increment_type_01', 'Salary by Employee'),
        ('increment_type_02', 'Increase by %'),
        ('increment_type_03', 'Increase by quantity'),
        ('increment_type_04', 'New General Salary'),
    ], compute='_compute_label_increase_amount')
    salary_employee_ids = fields.One2many('l10n.mx.salary.employee', 'modify_salary_id', 'Salary by Employee', index=True)
    state = fields.Selection([("draft", "Draft"), ("modify_salary", "Modify Salary")], default="draft", index=True)

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
                'integration_factor': self.truncate(type_benefit_line_id.integration_factor, 4),
                'l10n_mx_payroll_daily_salary': contract.l10n_mx_payroll_daily_salary,
                'l10n_mx_payroll_integrated_salary': contract.l10n_mx_payroll_integrated_salary,
                'state': 'draft',

            })
            salary_employee.append(salary_employee_id.id)
        res['salary_employee_ids'] = [(6, 0, salary_employee)]
        return res

    def truncate(self, number, max_decimals):
        int_part, dec_part = str(number).split(".")[0], str(number).split(".")[1]
        return float(".".join((int_part[0], dec_part[:max_decimals])))

    @api.depends('increment_type_id')
    def _compute_label_increase_amount(self):
        for record in self:
            if record.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_02').id:
                record.label_increase = 'increment_type_02'
            elif record.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_03').id:
                record.label_increase = 'increment_type_03'
            elif record.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_04').id:
                record.label_increase = 'increment_type_04'
            else:
                record.label_increase = 'increment_type_01'

    @api.onchange('increment_type_id')
    def _onchange_increment_type_id(self):
        if self.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_02').id:
            self.label_increase = 'increment_type_02'
            self.increase_amount = False
            self.increase_salary = False
        elif self.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_03').id:
            self.label_increase = 'increment_type_03'
            self.increase_percent = False
            self.increase_salary = False
        elif self.increment_type_id.id == self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_04').id:
            self.label_increase = 'increment_type_04'
            self.increase_percent = False
            self.increase_amount = False
        else:
            self.label_increase = 'increment_type_01'
            self.increase_percent = False
            self.increase_amount = False
            self.increase_salary = False

    def modify_salary(self):
        history_salary_employee_obj = self.env['l10n.mx.history.salary.employee']
        for line in self.salary_employee_ids.search([('apply', '=', True)]):
            l10n_mx_payroll_daily_salary_new = line.l10n_mx_payroll_daily_salary_new if line.l10n_mx_payroll_daily_salary_new != 0 else line.l10n_mx_payroll_daily_salary
            l10n_mx_payroll_integrated_salary_new = line.l10n_mx_payroll_integrated_salary_new if line.l10n_mx_payroll_integrated_salary_new != 0 else line.l10n_mx_payroll_integrated_salary
            line.contract_id.write({
                'l10n_mx_payroll_daily_salary': l10n_mx_payroll_daily_salary_new,
                'l10n_mx_payroll_integrated_salary': l10n_mx_payroll_integrated_salary_new,
            })
            history_salary_employee_id = history_salary_employee_obj.create({
                'contract_id': line.contract_id.id,
                'date': self.application_date,
                'l10n_mx_payroll_daily_salary_new': line.l10n_mx_payroll_daily_salary,
                'l10n_mx_payroll_integrated_salary_new': line.l10n_mx_payroll_integrated_salary,
                'state': 'modify',
            })
            line.contract_id.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
            line.write({'state_app': 'apply'})
        self.salary_employee_ids.sudo().search([('apply', '=', False)]).unlink()
        self.write({'state': 'modify_salary'})
        return True

    def update_increase(self):
        for line in self.salary_employee_ids.search([('apply', '=', True)]):
            if self.label_increase == 'increment_type_02':
                increase_percent = (line.l10n_mx_payroll_daily_salary * self.increase_percent) / 100
                l10n_mx_payroll_daily_salary_new = line.l10n_mx_payroll_daily_salary + increase_percent
            elif self.label_increase == 'increment_type_03':
                l10n_mx_payroll_daily_salary_new = line.l10n_mx_payroll_daily_salary + self.increase_amount
            elif self.label_increase == 'increment_type_04':
                l10n_mx_payroll_daily_salary_new = self.increase_salary
            elif self.label_increase == 'increment_type_01':
                l10n_mx_payroll_daily_salary_new = self.increase_salary
            line.l10n_mx_payroll_daily_salary_new = l10n_mx_payroll_daily_salary_new
            line.l10n_mx_payroll_integrated_salary_new = l10n_mx_payroll_daily_salary_new * line.integration_factor
        return True

    def action_check_apply(self):
        for line in self.salary_employee_ids:
            line.write({'apply': True})

    def action_not_check_apply(self):
        for line in self.salary_employee_ids:
            line.write({'apply': False})

    def unlink(self):
        for record in self:
            if record.state == 'modify_salary':
                raise ValidationError(_("The Salary Modification is done, therefore you cannot delete it."))
        return super(ModifySalary, self).unlink()


class SalaryEmployee(models.Model):
    _name = 'l10n.mx.salary.employee'
    _description = "Salary Employee"

    modify_salary_id = fields.Many2one('l10n.mx.modify.salary', string='Modify salary', index=True)
    apply = fields.Boolean(default=False, string='Apply', index=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
    employee_id = fields.Many2one('hr.employee', string='Employee', index=True)
    job_id = fields.Many2one('hr.job', string='Job', index=True)
    department_id = fields.Many2one('hr.department', string='Department', index=True)
    state = fields.Selection(related='contract_id.state', compute_sudo=True)
    l10n_mx_payroll_daily_salary = fields.Float(string='Daily Salary', index=True)
    l10n_mx_payroll_integrated_salary = fields.Float(string='Integrated Salary', index=True)
    type_salary = fields.Selection(related='contract_id.type_salary', compute_sudo=True)
    l10n_mx_date_imss = fields.Date(related='contract_id.l10n_mx_date_imss', compute_sudo=True)
    l10n_mx_antiquity = fields.Integer('Antiquity', compute="_compute_l10n_mx_antiquity")
    l10n_mx_type_benefit_id = fields.Many2one(related='contract_id.l10n_mx_type_benefit_id',
                                              compute_sudo=True)
    l10n_mx_holidays = fields.Integer(string="Days of holidays", compute='_compute_l10n_mx_contract_data')
    l10n_mx_vacation_bonus = fields.Integer(string="Vacation cousin (%)", compute='_compute_l10n_mx_contract_data')
    l10n_mx_christmas_bonus = fields.Integer(string="Bonus Days", compute='_compute_l10n_mx_contract_data')
    integration_factor = fields.Float(string='Integration Factor', digits=(16, 4), index=True)
    l10n_mx_payroll_daily_salary_new = fields.Float(string='SD New', digits=(16, 2), index=True)
    l10n_mx_payroll_integrated_salary_new = fields.Float(string='SBC New', digits=(16, 2), compute='_compute_l10n_mx_payroll_integrated_salary_new', readonly=False)
    state_app = fields.Selection([("draft", "Draft"), ("apply", "Apply"), ("not_apply", "Not Apply")], default="draft", string='Status Aplication', index=True)

    @api.depends('l10n_mx_payroll_daily_salary_new', 'integration_factor')
    def _compute_l10n_mx_payroll_integrated_salary_new(self):
        for record in self:
            record.l10n_mx_payroll_integrated_salary_new = record.integration_factor * record.l10n_mx_payroll_daily_salary_new

    @api.onchange('l10n_mx_payroll_daily_salary_new')
    def _onchange_l10n_mx_payroll_daily_salary_new(self):
        if self.l10n_mx_payroll_daily_salary_new < self.l10n_mx_payroll_daily_salary:
            raise ValidationError(_("The New SDI must be greater than the Daily Wage."))

    @api.onchange('l10n_mx_payroll_integrated_salary_new')
    def _onchange_l10n_mx_payroll_integrated_salary_new(self):
        if (self.l10n_mx_payroll_integrated_salary_new * self.integration_factor) < self.l10n_mx_payroll_integrated_salary_new:
            raise ValidationError(_("The New SBC must be greater than the Integrated Salary."))

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
