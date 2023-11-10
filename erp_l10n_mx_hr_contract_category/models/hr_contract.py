import logging
from odoo import fields, models,api

_logger = logging.getLogger(__name__)


class HrContract(models.Model):
    _inherit = 'hr.contract'

    category_id = fields.Many2one(
        'hr.contract.category',
        string='Category Contract',
    )
    status_not_apply = fields.Boolean(
        compute='_compute_status_not_apply',
        deafult=False,
    )

    def _compute_status_not_apply(self):
        salary_employee = self.env['l10n.mx.salary.employee']
        for contract in self:
            if salary_employee.search([('contract_id','=',contract.id),('state_app','=','not_apply')],limit=1):
                contract.status_not_apply=True
            else:
                contract.status_not_apply = False

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(HrContract, self).create(vals_list)
        history_salary_employee_id = self.env['l10n.mx.history.salary.employee'].sudo()
        for res in res_ids:
            if res.l10n_mx_date_imss:
                history_salary_employee_id.create({
                    'contract_id': res.id,
                    'date': res.l10n_mx_date_imss,
                    'category_id': self.category_id,
                    'contract_id_wage': self.wage,
                    'l10n_mx_payroll_daily_salary_new': res.l10n_mx_payroll_daily_salary,
                    'l10n_mx_payroll_integrated_salary_new': res.l10n_mx_payroll_integrated_salary,
                    'state': 'high',
                })
                res.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
        return res_ids

    def write(self, vals):
        res = super(HrContract, self).write(vals)
        history_salary = self.env['l10n.mx.history.salary.employee'].sudo()
        for contract in self:
            if 'state' in vals and vals['state'] in ('close', 'cancel'):
                history_salary_employee_id = history_salary.create({
                    'contract_id': contract.id,
                    'category_id': contract.category_id,
                    'contract_id_wage': contract.wage,
                    'date': fields.Datetime.now().date(),
                    'l10n_mx_payroll_daily_salary_new': contract.l10n_mx_payroll_daily_salary,
                    'l10n_mx_payroll_integrated_salary_new': contract.l10n_mx_payroll_integrated_salary,
                    'state': 'low',

                })
                contract.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
            if 'state' in vals and vals['state'] == 'open':
                history_salary_employee = contract.history_salary_employee_ids.search([], order='date desc', limit=1)
                if history_salary_employee.state == 'low':
                    history_salary_employee_id = history_salary.create({
                        'contract_id': contract.id,
                        'date': contract.l10n_mx_date_imss,
                        'category_id': contract.category_id,
                        'contract_id_wage': contract.wage,
                        'l10n_mx_payroll_daily_salary_new': contract.l10n_mx_payroll_daily_salary,
                        'l10n_mx_payroll_integrated_salary_new': contract.l10n_mx_payroll_integrated_salary,
                        'state': 're-entry',

                    })
                    contract.history_salary_employee_ids = [(4, history_salary_employee_id.id)]

        return res
