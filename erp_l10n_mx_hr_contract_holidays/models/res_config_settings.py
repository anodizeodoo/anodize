# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_automatic_sequence_contracts = fields.Boolean(
        related='company_id.l10n_mx_automatic_sequence_contracts',
        string='Contracts', readonly=False, compute_sudo=True)
    number_days_contracts = fields.Integer(related='company_id.number_days_contracts',
        string='Number Days', readonly=False, compute_sudo=True)

    contract_id_sequence = fields.Many2one(
        related="company_id.contract_id_sequence",
        readonly=False,
    )
