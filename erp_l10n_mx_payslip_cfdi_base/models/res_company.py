# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_minimum_wage = fields.Float(
        'Mexican minimum Wage',
        help='Indicates the current daily amount of the general minimum wage '
        'in Mexico')
    l10n_mx_uma = fields.Float(
        'Mexican UMA', help='Indicates the current UMA in Mexico')
    l10n_mx_umi = fields.Float(
        'Mexican UMI', help='Indicates the current UMI in Mexico')

    l10n_mx_stamped_version = fields.Selection(
        [('version_3', 'Version 3.3'), ('version_4', 'Version 4.0')], string='Stamped version',
        default='version_3')
