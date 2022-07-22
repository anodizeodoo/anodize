# -*- coding:utf-8 -*-

from odoo import api, fields, models, _


class HrEmployeeLevelStudies(models.Model):
    _name = 'hr.employee.level.studies'
    _description = 'Level of schooling'
    _sql_constraints = [
        ('name_uniq', 'UNIQUE(name)', 'Name must be unique!'),
    ]

    name = fields.Char('Name', translate=True)
    active = fields.Boolean(default=True, help="If the active field is set to False, it will allow you to hide without removing it.")
