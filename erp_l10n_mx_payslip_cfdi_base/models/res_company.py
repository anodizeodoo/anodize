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
        [('version_3', 'Version 3.3'),
         ('version_4', 'Version 4.0')],
        string='Stamped version',
        default='version_3')

    l10n_mx_stamp_receipt = fields.Boolean(string='Payroll receipt stamp', default=False)

    l10n_mx_stamp_receipt_readonly = fields.Boolean(compute='_compute_l10n_mx_stamp_receipt_readonly')

    work_fonacot = fields.Integer(string="Workplace FONACOT", tracking=True)

    def _compute_l10n_mx_stamp_receipt_readonly(self):
        pac_status_signed = self.env['hr.payslip'].search([('l10n_mx_pac_status', '=', 'signed')])
        if self.l10n_mx_stamp_receipt and len(pac_status_signed) > 0:
            self.l10n_mx_stamp_receipt_readonly = True
        else:
            self.l10n_mx_stamp_receipt_readonly = False
