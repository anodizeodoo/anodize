from odoo import fields, models, api


class HrEmployeeRelative(models.Model):
    _inherit = 'hr.employee.relative'

    scholarship_grade_id = fields.Many2one(
        'hr.scholarship.grade',
        string='Grade'
    )
