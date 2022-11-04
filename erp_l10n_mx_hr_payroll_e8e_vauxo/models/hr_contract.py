# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    type_salary = fields.Selection([('fixed', '01-Fixed'), ('variable', '02-Variable'), ('mixed', '03-Mixed')],
                                   string='Type salary', default='fixed')
