# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _


class InsuranceBranch(models.Model):
    _name = "l10n.mx.insurance.branch"
    _description = 'Insurance branch'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    is_work_risk = fields.Boolean(string='Is work risk')
