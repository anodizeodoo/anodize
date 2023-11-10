# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import base64
import logging
import re
import time
from io import BytesIO
from itertools import groupby
from calendar import monthrange
import requests

from lxml import etree, objectify
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)


class HrPayslipInability(models.Model):
    _name = 'hr.payslip.inability'
    _description = 'Pay Slip inability'

    payslip_id = fields.Many2one(
        'hr.payslip', required=True, ondelete='cascade',
        help='Payslip related with this inability')
    sequence = fields.Integer(required=True, default=10)
    days = fields.Integer(
        help='Number of days in which the employee performed inability in '
        'the payslip period', required=True, index=True)
    inability_type = fields.Selection(
        [('01', 'Risk of work'),
         ('02', 'Disease in general'),
         ('03', 'Maternity'),
         ('04', 'License for medical care of children diagnosed with cancer.')
         ], 'Type', required=True, default='01', index=True,
        help='Reason for inability: Catalog published in the SAT portal')
    amount = fields.Float(help='Amount for the inability', required=True, index=True)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    l10n_mx_inability_line_ids = fields.One2many(
        'hr.payslip.inability', 'payslip_id', 'Inabilities',
        readonly=True, states={'draft': [('readonly', False)]},
        help='Used in XML like optional node to express disabilities '
        'applicable by employee.', copy=True)
    count_inability = fields.Integer(string='Cantidad', compute='_compute_count_inability')

    def _compute_count_inability(self):
        for record in self:
            record.count_inability = sum(record.l10n_mx_inability_line_ids.mapped('days'))		

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(HrPayslip, self).create(vals_list)
        # TODO perform this to sql method and before save set inabilities
        insurance_branch_1 = self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_1').id
        insurance_branch_2 = self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_2').id
        insurance_branch_6 = self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_6').id
        for res in res_ids:
            leave_ids = self.env['hr.leave'].search([
                ('type', '=', 'disabilities'),
                ('request_date_from', '>=', res.date_from),
                ('request_date_to', '<=', res.date_to),
                ('employee_id', '=', res.employee_id.id)
            ])
            inability_lines = []
            for leave in leave_ids:
                if leave.insurance_branch_id.id == insurance_branch_1:
                    inability_type = '01'
                elif leave.insurance_branch_id.id == insurance_branch_2:
                    inability_type = '02'
                elif leave.insurance_branch_id.id == insurance_branch_6:
                    inability_type = '04'
                else:
                    inability_type = '03'
                inability_lines.append((0, 0, {
                    'days': int(leave.number_of_days),
                    'inability_type': inability_type,
                    'amount': leave.amount,
                }))
            res.write({'l10n_mx_inability_line_ids': inability_lines})
        return res_ids

    def action_open_inability(self):
        self.ensure_one()
        return {
            'name': 'Incapacidades',
            'view_mode': 'tree',
            'res_model': 'hr.payslip.inability',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'domain': [('payslip_id', '=', self.id)],
            'context': {'default_payslip_id': self.id},
        }
