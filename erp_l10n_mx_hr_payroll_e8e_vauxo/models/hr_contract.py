# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _


class HrContract(models.Model):
    _inherit = 'hr.contract'

    type_salary = fields.Selection([('fixed', '01-Fixed'),
                                    ('variable', '02-Variable'),
                                    ('mixed', '03-Mixed')],
                                   tracking=True,
                                   string='Type salary', default='fixed')

class HrEmployee(models.Model):
    _inherit = "hr.employee"


    #  Payments
    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method',
                                                    string="Payment Way",
                                                    help="Indicates the way the invoice was/will be paid, where the options could be: "
                                                         "Cash, Nominal Check, Credit Card, etc. Leave empty if unkown and the XML will show 'Unidentified'.",
                                                    default=lambda self: self.env.ref(
                                                        'l10n_mx_edi.payment_method_otros', raise_if_not_found=False))