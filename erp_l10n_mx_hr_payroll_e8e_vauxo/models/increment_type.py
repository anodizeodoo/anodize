# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class IncrementType(models.Model):
    _name = "l10n.mx.increment.type"
    _description = "Increment Type"

    name = fields.Char(string='Name', translate=True)

