# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    is_extra_hours = fields.Boolean(string='Extra Hours', related='company_id.is_extra_hours', readonly=False, compute_sudo=True)
