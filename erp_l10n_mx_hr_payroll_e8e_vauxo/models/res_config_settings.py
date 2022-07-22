# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_payroll_receipt_format = fields.Selection(
        [('sat_receipt', 'SAT Receipt'), ('other_receipt', 'Other Receipt')], string='Receipt',
        related='company_id.l10n_mx_payroll_receipt_format',
        readonly=False)
