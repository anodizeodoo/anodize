# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


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
