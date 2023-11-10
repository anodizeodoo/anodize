# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ShedulePay(models.Model):
    _name = "l10n.mx.payroll.schedule.pay"
    _description = "Schedule Pay"

    code = fields.Char(string='Code', index=True)
    name = fields.Char(string='Name', translate=True, index=True)
    day_payment = fields.Integer(string='Day Payment', index=True)
