# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_edi_employer_registration_id = fields.Many2one(related='company_id.l10n_mx_edi_employer_registration_id', readonly=False)