# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeHealthConditionType(models.Model):
    _name = 'hr.employee.health.condition.type'
    _description = 'HR Employee Health Condition Type'

    name = fields.Char(
        string='Type',
        required=True,
        translate=True
    )
