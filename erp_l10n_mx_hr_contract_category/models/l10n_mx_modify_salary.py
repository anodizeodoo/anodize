from dateutil.relativedelta import relativedelta
from datetime import datetime

from odoo import fields, models,api, _


class ModifySalary(models.Model):
    _inherit = 'l10n.mx.modify.salary'

    date_day = fields.Date(
        string='Date Now',
        copy=False,
        default=lambda s: fields.Date.today()
    )

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
                'category_id': contract.category_id.id,
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

    def action_employees_search(self):
        self.ensure_one()
        return {
            'name': _('Salary Employee'),
            'view_mode': 'tree',
            'domain': [('id', 'in', self.mapped('salary_employee_ids').ids)],
            'res_model': 'l10n.mx.salary.employee',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

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
                'category_id': line.category_id.id,
                'contract_id_wage': line.wage_manual,
                'l10n_mx_payroll_daily_salary_new': line.l10n_mx_payroll_daily_salary,
                'l10n_mx_payroll_integrated_salary_new': line.l10n_mx_payroll_integrated_salary,
                'state': 'modify',
            })
            line.contract_id.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
            line.write({'state_app': 'apply'})
        self.salary_employee_ids.sudo().search([('apply', '=', False)]).unlink()
        self.write({'state': 'modify_salary'})
        return True

