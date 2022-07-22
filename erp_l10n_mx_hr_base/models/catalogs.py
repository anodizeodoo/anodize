# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _

class L10nMxEdiJobRank(models.Model):
    _name = "l10n_mx_edi.job.risk"
    _description = "Used to define the percent of each job risk."

    name = fields.Char(help='Job risk provided by the SAT.')
    code = fields.Char(help='Code assigned by the SAT for this job risk.')
    percentage = fields.Float(help='Percentage for this risk, is used in the '
                              'payroll rules.', digits=(2, 6),)