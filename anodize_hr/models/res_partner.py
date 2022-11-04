# coding: utf-8
from odoo import fields, api, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def _update_fields_values(self, fields):
        values = super(ResPartner, self)._update_fields_values(fields)
        values.update({'vat': False})
        return values