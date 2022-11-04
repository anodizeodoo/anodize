# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_automatic_sequence_contracts = fields.Boolean(
        related='company_id.l10n_mx_automatic_sequence_contracts',
        string='Contracts', readonly=False)
