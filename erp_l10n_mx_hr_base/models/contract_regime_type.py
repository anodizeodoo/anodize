# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ContractRegimeType(models.Model):
    _name = "l10n.mx.edi.contract.regime.type"
    _description = "Contract Type"

    name = fields.Char(string='Name', index=True)
    code = fields.Char(string='Code', index=True)
    date = fields.Date(string='Validity start date', index=True)
