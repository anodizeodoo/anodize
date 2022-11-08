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
from werkzeug import url_encode
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def get_cfdi_employee_data(self, contract):
        self.ensure_one()
        return {
            'contract_type': contract.l10n_mx_payroll_contract_type_id.code,
            'emp_syndicated': 'Sí' if self.l10n_mx_edi_syndicated else 'No',
            'working_day': self.get_working_date(),
            'emp_diary_salary': '%.2f' % contract.
                l10n_mx_payroll_integrated_salary,
        }

    def get_working_date(self):
        """Based on employee category, verify if a category set in this
        employee come from this module and get code."""
        category = self.category_ids.filtered(lambda r: r.color == 3)
        if not category or not category[0].get_external_id()[
            category[0].id].startswith('erp_l10n_mx_hr_base.hr_payroll_employee'):
            return ''
        return category[0].name[:2]

class HrEmployeeLoan(models.Model):
    _inherit = 'hr.employee.loan'

    payslip_ids = fields.Many2many(
        'hr.payslip', help='Payslips where this loan is collected.')
    payslips_count = fields.Integer(
        'Number of Payslips', compute='_compute_payslips_count', compute_sudo=True)

    def _compute_payslips_count(self):
        for loan in self:
            loan.payslips_count = len(loan.payslip_ids.filtered(
                lambda rec: rec.state == 'done'))

    def action_get_payslips_view(self):
        return {
            'name': _('Loan Payslips'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.payslip',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.payslip_ids.filtered(
                lambda rec: rec.state == 'done').ids)],
        }