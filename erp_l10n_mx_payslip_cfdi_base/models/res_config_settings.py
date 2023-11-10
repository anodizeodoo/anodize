# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_minimum_wage = fields.Float(
        related='company_id.l10n_mx_minimum_wage',
        string='Mexican minimum salary', readonly=False, compute_sudo=True,
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')
    l10n_mx_uma = fields.Float(
        related='company_id.l10n_mx_uma', compute_sudo=True,
        string='Mexican UMA', readonly=False,
        help='Indicates the current UMA in Mexico')
    l10n_mx_umi = fields.Float(
        related='company_id.l10n_mx_umi', compute_sudo=True,
        string='Mexican UMI', readonly=False, help='Indicates the current UMI in Mexico')
    l10n_mx_stamped_version = fields.Selection(related='company_id.l10n_mx_stamped_version',
                                               string='Stamped version', readonly=False, compute_sudo=True)
    l10n_mx_stamp_receipt = fields.Boolean(related='company_id.l10n_mx_stamp_receipt', string='Payroll receipt stamp', readonly=False, compute_sudo=True)
    l10n_mx_stamp_receipt_readonly = fields.Boolean(related='company_id.l10n_mx_stamp_receipt_readonly', compute_sudo=True)

    work_fonacot = fields.Integer(related='company_id.work_fonacot', readonly=False, compute_sudo=True)