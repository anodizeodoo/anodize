# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ContractRegimeType(models.Model):
    _name = "l10n.mx.edi.contract.regime.type"
    _description = "Contract Type"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    date = fields.Date(string='Validity start date')
