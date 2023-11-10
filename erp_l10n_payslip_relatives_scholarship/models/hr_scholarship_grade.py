from odoo import fields, models


class HrScholarshipGrade(models.Model):
    _inherit = 'hr.scholarship.grade'

    salary_rule = fields.Many2one(
        'hr.salary.rule',
        string='Salary Rule',
        domain=[('active_rule_sh', '=', True)],
        required=True
    )
