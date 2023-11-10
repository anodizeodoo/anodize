# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeRelativeProfessions(models.Model):
    _name = 'hr.employee.relative.professions'
    _description = 'HR Employee Relative Professions'

    name = fields.Char(
        string='Nombre',
        required=True,
        index=True)

    code = fields.Char(
        string='Código',
        index = True)

    active = fields.Boolean('Activo', default=True, index=True)