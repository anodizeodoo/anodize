# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployeeBloodType(models.Model):
    _name = 'hr.employee.blood.type'
    _description = 'HR Employee Blood Type'

    name = fields.Char(
        string='Type',
        required=True,
        translate=True
    )
