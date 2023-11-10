# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class DisabilityControl(models.Model):
    _name = "l10n.mx.disability.control"
    _description = 'Disability Control'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
