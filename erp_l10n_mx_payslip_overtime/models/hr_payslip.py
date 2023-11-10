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

    name = fields.Char('Description', required=True, index=True)
    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related.', index=True)
    days = fields.Integer(
        help="Number of days in which the employee performed overtime in the "
        "period", required=True, index=True)
    hours = fields.Integer(
        help="Number of overtime hours worked in the period", required=True, index=True)
    overtime_type_id = fields.Many2one('hr.type.overtime', string='Type', required=True, index=True,
        help='Used to express the type of payment of the hours extra.')
    amount = fields.Float(
        help="Amount paid for overtime", required=True, default=0.0, index=True)

    @api.constrains('hours')
    def _check_value_zero(self):
        for record in self:
            if (record.hours == 0):
                raise ValidationError(_('The field hours in the overtime section cannot have value 0.'))


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    l10n_mx_overtime_line_ids = fields.One2many(
        'hr.register.overtime.line', 'payslip_id', 'Extra hours',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Used in XML like optional node to express the extra hours '
             'applicable by employee.', copy=True)

    count_overtime = fields.Float(string='Cantidad', compute='_compute_count_overtime')

    def _compute_count_overtime(self):
        for record in self:
            record.count_overtime = sum(record.l10n_mx_overtime_line_ids.mapped('work_hour'))

    def action_open_overtime(self):
        self.ensure_one()
        return {
            'name': 'Horas extras',
            'view_mode': 'tree,form',
            'res_model': 'hr.register.overtime.line',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('payslip_id', '=', self.id)],
            'context': {'default_payslip_id': self.id}
        }

