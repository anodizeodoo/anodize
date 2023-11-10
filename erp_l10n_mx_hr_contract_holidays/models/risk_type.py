# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class RiskType(models.Model):
    _name = "l10n.mx.risk.type"
    _description = 'Risk type'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
