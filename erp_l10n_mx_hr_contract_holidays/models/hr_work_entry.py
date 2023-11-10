# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class HrWorkEntryType(models.Model):
    _inherit = 'hr.work.entry.type'
    _description = 'HR Work Entry Type'

    is_vacation = fields.Boolean(string='Vacation', default=False)
    is_vacation_bonus = fields.Boolean(string='Vacation bonus', default=False)
