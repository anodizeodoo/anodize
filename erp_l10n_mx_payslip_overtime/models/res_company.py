# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResCompany(models.Model):
    _inherit = "res.company"

    is_extra_hours = fields.Boolean(string='Extra Hours', default=False)

    @api.onchange('is_extra_hours')
    def _onchange_is_extra_hours(self):
        contract_ids = self.env['hr.contract'].search([('company_id', '=', self.id)])
        contract_ids.write({'is_extra_hours': self.is_extra_hours})
