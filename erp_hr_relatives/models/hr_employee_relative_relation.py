# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeRelativeRelation(models.Model):
    _name = 'hr.employee.relative.relation'
    _description = 'HR Employee Relative Relation'

    name = fields.Char(
        string='Relation',
        required=True,
        index=True)

    code = fields.Char(
        string='Código',
        index = True)

    active = fields.Boolean('Activo', default=True, index=True)