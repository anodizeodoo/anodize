# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class HrLeaveTypeConsidered(models.Model):
    _name = "hr.leave.type.considered"
    _description = 'It is considered'

    def _default_code(self):
        sequence_id = self.env['ir.sequence'].search([('code', '=', 'hr.leave.type.considered')])
        if sequence_id:
            return sequence_id.get_next_char(sequence_id.number_next_actual)
        return False

    code = fields.Char(string='Code', default=lambda self: self._default_code())
    name = fields.Char(string='Name')

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['code'] = self.env['ir.sequence'].next_by_code('hr.leave.type.considered')
        return super(HrLeaveTypeConsidered, self).create(vals_list)