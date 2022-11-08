# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class TableUMAS(models.Model):
    _name = "l10n.mx.table.umas"
    _description = 'UMAS'
    _rec_name = 'date_start'

    date_start = fields.Date(string='Date Start')
    value_uma = fields.Float(string='Value UMA')
    status = fields.Boolean(string='Status')