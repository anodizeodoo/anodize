from odoo import fields, models, api, _


class HrContractCategory(models.Model):
    _name = 'hr.contract.category'
    _description = 'Hr Contract Category'
    _inherit = ['mail.thread','mail.activity.mixin']

    code = fields.Char(
        string='Code', tracking=True,
        required=True,
    )

    name = fields.Char(
        string='Name', tracking=True,
        required=True
    )

    amount_salary_day = fields.Float(
        string='Salary Day(SD)', tracking=True,
        required=True,
    )

    count_employee = fields.Integer(
        string='Total Employee',
        compute='_compute_count_employee',
        store=True,
    )

    employee_ids = fields.One2many(
        'hr.employee',
        'category_contract_id',
        string='Employees',
    )

    active = fields.Boolean(
        string='Active', tracking=True,
        default=True,
    )

    @api.depends('employee_ids')
    def _compute_count_employee(self):
        for category in self:
            category.count_employee = len(category.employee_ids)

    def action_employees_views(self):
        self.ensure_one()
        return {
            'name': _('Employee'),
            'view_mode': 'tree,form',
            'domain': [('id', 'in', self.mapped('employee_ids').ids)],
            'res_model': 'hr.employee',
            'type': 'ir.actions.act_window',
            'context': {'create': False, 'active_test': False},
        }

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrContractCategory, self).create(vals_list)
        res.cretate_modify_salary(res)
        return res

    def cretate_modify_salary(self, records):
        modify_salary = self.env['l10n.mx.modify.salary'].sudo()
        increment_type = self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.increment_type_01').id
        for record in records:
            created = modify_salary.create(
                {
                    'application_date': fields.Date.today(),
                    'increment_type_id': increment_type
                }
            )
            if created:
                for employee_salary in created.mapped('salary_employee_ids'):
                    employee_salary.write({
                        'category_id': record.id,
                        'state_app': 'not_apply'
                    })

    
