# -*- coding:utf-8 -*-
from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _default_number(self):
        if getattr(self.env.user.company_id, "is_sequence", False):
            if self.env.user.company_id.is_sequence:
                # sequence_id = self.env['ir.sequence'].search([('code', '=', 'hr.employee.number')], limit=1)
                sequence_id = self.env.user.company_id.employee_id_sequence
                if sequence_id:
                    return sequence_id.get_next_char(sequence_id.number_next_actual)
        return False

    number = fields.Char(default=lambda self: self._default_number(),
                         string='No. Employee',
                         index=True)
    registration_number = fields.Char(default=lambda self: self._default_number(), index=True)
    is_sequence = fields.Boolean(related="company_id.is_sequence", compute_sudo=True)

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.user.company_id.is_sequence:
            for vals in vals_list:
                sequence_id = self.env.user.company_id.employee_id_sequence
                code = sequence_id.code
                number = self.env["ir.sequence"].next_by_code(code)
                vals["number"] = number
                vals["registration_number"] = number
        return super(HrEmployee, self).create(vals_list)


class HrEmployeePublic(models.Model):
    _name = "hr.employee.public"
    _inherit = 'hr.employee.public'

    number = fields.Char(readonly=True)
    registration_number = fields.Char(readonly=True)

