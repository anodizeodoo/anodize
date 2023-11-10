# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_payroll_receipt_format = fields.Selection(
        [('sat_receipt', 'SAT Receipt'), ('other_receipt', 'Other Receipt')], string='Receipt',
        default='sat_receipt')
