# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class LoanType(models.Model):
    _name = "l10n.mx.loan.type"
    _description = "Loan Type"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    active = fields.Boolean(string='Active', default=True)
    rule_id = fields.Many2one('hr.salary.rule', string='Rule')

