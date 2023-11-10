# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class TableHolidays(models.Model):
    _name = "l10n.mx.table.holidays"
    _description = 'Holidays'

    l10n_mx_year = fields.Integer(string='Years')
    l10n_mx_days = fields.Integer(string='Days for years')
    l10n_mx_rule_value_init = fields.Integer(string='Rule value init month')
    l10n_mx_rule_value_end = fields.Integer(string='Rule value end month')

    def find_rule_by_month(self, month):
        domain = [('l10n_mx_rule_value_init', '<=', month), ('l10n_mx_rule_value_end', '>=', month)]
        rule = self.search(domain, limit=1)
        return rule
