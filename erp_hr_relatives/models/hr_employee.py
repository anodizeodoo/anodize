# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    relative_ids = fields.One2many(
        string='Relatives',
        comodel_name='hr.employee.relative',
        inverse_name='employee_id',
        context={'active_test': False},
    )