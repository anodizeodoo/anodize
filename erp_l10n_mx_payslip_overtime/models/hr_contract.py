# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    history_overtime_ids = fields.One2many('hr.register.overtime.line', 'contract_id', 'Extra Hours')
    is_extra_hours = fields.Boolean(string='Extra Hours', default=False, index=True)

