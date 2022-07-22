# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)

class HrPayslipOvertime(models.Model):
    _name = 'hr.payslip.overtime'
    _description = 'Pay Slip overtime'

    name = fields.Char('Description', required=True)
    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.')
    days = fields.Integer(
        help="Number of days in which the employee performed overtime in the "
        "period", required=True)
    hours = fields.Integer(
        help="Number of overtime hours worked in the period", required=True)
    overtime_type = fields.Selection([
        ('01', 'Double'),
        ('02', 'Triples'),
        ('03', 'Simples')], 'Type', required=True, default='01',
        help='Used to express the type of payment of the hours extra.')
    amount = fields.Float(
        help="Amount paid for overtime", required=True, default=0.0)

    @api.constrains('hours')
    def _check_value_zero(self):
        for record in self:
            if (record.hours == 0):
                raise ValidationError(_('The field hours in the overtime section cannot have value 0.'))


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    l10n_mx_overtime_line_ids = fields.One2many(
        'hr.payslip.overtime', 'payslip_id', 'Extra hours',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Used in XML like optional node to express the extra hours '
             'applicable by employee.', copy=True)