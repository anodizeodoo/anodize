# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class Sequel(models.Model):
    _name = "l10n.mx.sequel"
    _description = 'Sequel'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
