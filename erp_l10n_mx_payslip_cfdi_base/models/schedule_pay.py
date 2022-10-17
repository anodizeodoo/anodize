# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ShedulePay(models.Model):
    _inherit = "l10n.mx.payroll.schedule.pay"

    l10n_mx_table_isr_id = fields.Many2one('l10n.mx.table.isr', string='ISR')
