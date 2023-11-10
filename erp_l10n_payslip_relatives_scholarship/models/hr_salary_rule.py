from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    active_rule_sh = fields.Boolean('Active for Scholarship', default=True)
