# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class TypeBenefit(models.Model):
    _name = "l10n.mx.type.benefit"
    _description = "Types of Benefits"

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    day_year = fields.Integer(string='Days for years')
    day_month = fields.Integer(string='Days for month')
    type_benefit_line_ids = fields.One2many('l10n.mx.type.benefit.line',
                                            'type_benefit_id', 'Types of Benefits line')

    def find_rule_by_antiquity(self, antiquity):
        last_type_benefit_line_start = self.env.ref('erp_l10n_mx_hr_base.benefit_type_line_1')
        last_type_benefit_line_end = self.env.ref('erp_l10n_mx_hr_base.benefit_type_line_29')

        domain = [('antiquity', '=', antiquity),
                  ('type_benefit_id', '=', self.sudo().id)]
        # rule = self.type_benefit_line_ids.search(domain, limit=1)
        rule = self.env['l10n.mx.type.benefit.line'].sudo().search(domain, limit=1)

        if antiquity > last_type_benefit_line_end.antiquity and not rule:
            rule = last_type_benefit_line_end
        elif antiquity < last_type_benefit_line_end.antiquity and not rule:
            rule = last_type_benefit_line_start

        return rule


class TypeBenefitLine(models.Model):
    _name = "l10n.mx.type.benefit.line"
    _description = "Types of Benefits line"

    type_benefit_id = fields.Many2one('l10n.mx.type.benefit', 'Type of Benefits')
    antiquity = fields.Integer(string='Antiquity')
    holidays = fields.Integer(string='Holidays')
    vacation_cousin = fields.Integer(string='Vacation cousin (%)')
    bonus_days = fields.Integer(string='Bonus Days')
    holidays2 = fields.Float(string='Holidays', compute='_compute_holidays2')
    total_days = fields.Float(string='Total days', compute='_compute_total_days')
    integration_factor = fields.Float(string='Integration Factor',
                                      compute='_compute_integration_factor', digits=(16, 9))

    @api.depends('holidays', 'vacation_cousin')
    def _compute_holidays2(self):
        for record in self:
            if record.holidays and record.vacation_cousin:
                record.holidays2 = record.holidays * (record.vacation_cousin / 100)
            else:
                record.holidays2 = False

    @api.depends('type_benefit_id.day_year', 'bonus_days', 'holidays2')
    def _compute_total_days(self):
        for record in self:
            record.total_days = record.type_benefit_id.day_year + record.bonus_days + record.holidays2

    @api.depends('type_benefit_id.day_year', 'total_days')
    def _compute_integration_factor(self):
        for record in self:
            if record.type_benefit_id.day_year and record.total_days:
                record.integration_factor = record.total_days / record.type_benefit_id.day_year
            else:
                record.integration_factor = False