# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class TableUMI(models.Model):
    _name = "l10n.mx.table.umi"
    _description = 'UMI'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Date Start')
    value_umi = fields.Float(string='Value UMI')
    status = fields.Boolean(string='Status')
    year = fields.Char(string='Year', default=lambda self: str(fields.Date.today().year))
