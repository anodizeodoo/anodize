# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class TableIsr(models.Model):
    _name = "l10n.mx.table.isr"
    _description = 'ISR'
    _rec_name = 'l10n_mx_isr_name'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year + 1, 2000, -1)]

    l10n_mx_isr_name = fields.Char(string='Name',
                                   compute='_compute_l10n_mx_isr_name', store=True,
                                   index=True, translate=True)
    l10n_mx_isr_year = fields.Selection(string='Years', selection=_get_years,
                                        default=str(datetime.now().year))
    l10n_mx_isr_type = fields.Selection([('DAILY', 'DAILY'),
                                         ('WEEKLY', 'WEEKLY'),
                                         ('DECENNIAL', 'DECENNIAL'),
                                         ('BIWEEKLY', 'BIWEEKLY'),
                                         ('MONTHLY', 'MONTHLY'),
                                         ('ANNUAL', 'ANNUAL')], string='Type')
    l10n_mx_isr_rate_ids = fields.One2many('l10n.mx.table.isr.rate',
                                           'l10n_mx_table_isr_id',
                                           string='Rate ISR')
    l10n_mx_isr_subsidy_rate_ids = fields.One2many('l10n.mx.table.isr.subsidy.rate',
                                                   'l10n_mx_table_isr_id',
                                                   string='Subsidy rate')

    @api.depends('l10n_mx_isr_type')
    def _compute_l10n_mx_isr_name(self):
        for isr in self:
            if isr.sudo().l10n_mx_isr_type:
                isr.l10n_mx_isr_name = 'ISR {}'.format(isr.sudo().l10n_mx_isr_type)
            else:
                isr.l10n_mx_isr_name = 'ISR'

    def find_rule_by_rate(self, value):
        domain = [('l10n_mx_isr_rate_lower_limit', '<=', value),
                  ('l10n_mx_isr_rate_upper_limit', '>=', value),
                  ('l10n_mx_table_isr_id', '=', self.sudo().id)]
        # rule = self.l10n_mx_isr_rate_ids.sudo().search(domain, limit=1)
        rule = self.env['l10n.mx.table.isr.rate'].sudo().search(domain, limit=1)
        return rule

    def find_rule_by_subsidy(self, value):
        domain = [('l10n_mx_isr_subsidy_income_from', '<=', value),
                  ('l10n_mx_isr_subsidy_income_of', '>=', value),
                  ('l10n_mx_table_isr_id', '=', self.sudo().id)]
        # rule = self.l10n_mx_isr_subsidy_rate_ids.search(domain, limit=1)
        rule = self.env['l10n.mx.table.isr.subsidy.rate'].sudo().search(domain, limit=1)

        return rule


class TableIsrRate(models.Model):
    _name = "l10n.mx.table.isr.rate"
    _description = 'Rate ISR'

    l10n_mx_table_isr_id = fields.Many2one('l10n.mx.table.isr', string='Table ISR')
    l10n_mx_isr_rate_lower_limit = fields.Float(string='Lower limit')
    l10n_mx_isr_rate_upper_limit = fields.Float(string='Upper limit')
    l10n_mx_isr_rate_fixed_fee = fields.Float(string='Fixed fee')
    l10n_mx_isr_rate_percentage = fields.Float(string='Percentage')


class TableIsrSubsidyRate(models.Model):
    _name = "l10n.mx.table.isr.subsidy.rate"
    _description = 'Subsidy Rate'

    l10n_mx_table_isr_id = fields.Many2one('l10n.mx.table.isr', string='Table ISR')
    l10n_mx_isr_subsidy_income_from = fields.Float(string='For income from')
    l10n_mx_isr_subsidy_income_of = fields.Float(string='Up to income of')
    l10n_mx_isr_subsidy_quantity = fields.Float(string='Subsidy quantity')