# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _
from odoo.osv import expression


class SatKeys(models.Model):
    _name = "l10n.mx.sat.keys"
    _description = 'SAT keys'
    _rec_name = 'l10n_mx_sat_name'

    l10n_mx_sat_code = fields.Char(string='Code')
    l10n_mx_sat_name = fields.Char(string='Name', translate=True)
    l10n_mx_sat_classification = fields.Selection([
        ('perception', 'Perception'),
        ('deduction', 'Deduction'),
        ('other', 'Other payments')
    ], string="Classification")
    l10n_mx_sat_date_start = fields.Date(string='Start Date of Validity')
    l10n_mx_sat_date_end = fields.Date(string='End of Validity Date')
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', default=10)

    def name_get(self):
        res = []
        for rec in self:
            if rec.l10n_mx_sat_code:
                res.append((rec.id, "%s - %s" % (str(rec.l10n_mx_sat_code), rec.l10n_mx_sat_name)))
            else:
                res.append((rec.id, rec.l10n_mx_sat_name))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('l10n_mx_sat_name', 'ilike', name), ('l10n_mx_sat_code', 'ilike', name)]
        return self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)

