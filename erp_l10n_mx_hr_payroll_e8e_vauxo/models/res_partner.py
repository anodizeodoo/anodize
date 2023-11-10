# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re
from odoo import fields, models, api
from unicodedata import normalize


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _get_return_without_accent(self, word):
        word = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", normalize("NFD", word),
                      0, re.I)
        word = normalize('NFC', word)
        return word

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name') and vals.get('employee'):
                vals.update({'name': self._get_return_without_accent(vals.get('name')).upper()})
        return super(ResPartner, self).create(vals_list)

    def write(self, vals):
        employees_partners = self.sudo().filtered(lambda s: s.employee)
        if vals.get('name') and len(employees_partners) == len(self.ids):
            vals.update({'name': self._get_return_without_accent(vals.get('name')).upper()})
        return super(ResPartner, self).write(vals)

    def action_update_partner_name(self):
        for record in self.filtered(lambda s: s.employee):
            record.name = self._get_return_without_accent(record.name).upper()

