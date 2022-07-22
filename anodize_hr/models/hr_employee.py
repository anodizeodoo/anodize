# -*- coding:utf-8 -*-

from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _default_number(self):
        sequence_id = self.env['ir.sequence'].search([('code', '=', 'hr.employee.number')])
        if sequence_id:
            return sequence_id.get_next_char(sequence_id.number_next_actual)
        return False

    number = fields.Char(default=lambda self: self._default_number(), string='No. Employee')
    level_studies_id = fields.Many2one('hr.employee.level.studies', string='Level of schooling')
    registration_number = fields.Char(default=lambda self: self._default_number())

    @api.model
    def create(self, vals):
        number = self.env["ir.sequence"].next_by_code("hr.employee.number")
        vals["number"] = number
        vals["registration_number"] = number
        return super(HrEmployee, self).create(vals)
