# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class TableMinimumWage(models.Model):
    _name = "l10n.mx.table.minimum.wage"
    _description = 'Minimum wage'
    _rec_name = 'date_effective'

    date_effective = fields.Date(string='Effective date', index=True)
    zone_a = fields.Float(string='Zone A', index=True)
    zone_b = fields.Float(string='Zone B', index=True)
    zone_c = fields.Float(string='Zone C', index=True)
    status = fields.Boolean(string='Status', index=True)
    year = fields.Char(string='Year', default=lambda self: str(fields.Date.today().year), index=True)
