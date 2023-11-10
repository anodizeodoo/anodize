# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    code = fields.Char('Code')
    considered_id = fields.Many2one('hr.leave.type.considered', string='It is considered')
    decreases_seventh_day = fields.Boolean(string='Decreases from the seventh day')
