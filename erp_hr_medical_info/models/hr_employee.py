# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    health_condition_ids = fields.One2many(
        string='Health Conditions',
        comodel_name='hr.employee.health.condition',
        inverse_name='employee_id',
        groups='base.group_user',
    )
    blood_type = fields.Many2one(
        string='Blood Type',
        comodel_name='hr.employee.blood.type',
        groups='base.group_user',
    )
    health_notes = fields.Text(
        string='Health Notes',
        groups='base.group_user',
    )
