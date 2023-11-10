# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeHealthConditionSeverity(models.Model):
    _name = 'hr.employee.health.condition.severity'
    _description = 'HR Employee Health Condition Severity'

    name = fields.Char(
        string='Severity',
        required=True,
        translate=True
    )
