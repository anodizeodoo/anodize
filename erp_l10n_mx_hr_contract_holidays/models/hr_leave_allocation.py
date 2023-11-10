# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
