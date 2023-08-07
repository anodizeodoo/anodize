# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class GenerateHolidaysWizard(models.TransientModel):
    _name = 'generate.holidays.wizard'
    _description = 'Generate holidays wizard'

    holidays_employee_ids = fields.One2many('generate.holidays.line.wizard', 'holidays_employee_id', 'Holidays Employee Lines')
    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')

    @api.model
    def default_get(self, fields):
        res = super(GenerateHolidaysWizard, self).default_get(fields)
        contract_ids = self.env['hr.contract'].search([('state', '=', 'open')])
        holidays_employee_obj = self.env['generate.holidays.line.wizard']
        leave_allocation_obj = self.env['hr.leave.allocation']
        holidays_employee = []
        for contract in contract_ids:
            leave_allocation_id = leave_allocation_obj.sudo().search([
                ('contract_id', '=', contract.id),
                ('employee_id', '=', contract.employee_id.id),
                ('holiday_status_id', '=', self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id)
            ])
            if not leave_allocation_id:
                holidays_employee_id = holidays_employee_obj.create({
                    'contract_id': contract.id,
                    'employee_id': contract.employee_id.id,
                    'holidays_employee_id': self.id,
                    'apply': False,
                })
                holidays_employee.append(holidays_employee_id.id)
        if len(holidays_employee) > 0:
            res['holidays_employee_ids'] = [(6, 0, holidays_employee)]
        return res

    def action_check_apply(self):
        for line in self.holidays_employee_ids:
            line.write({'apply': True})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate holidays'),
            'res_model': 'generate.holidays.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def action_not_check_apply(self):
        for line in self.holidays_employee_ids:
            line.write({'apply': False})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate holidays'),
            'res_model': 'generate.holidays.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }

    def generate_holidays(self):
        leave_allocation_obj = self.env['hr.leave.allocation']
        holidays_contract_obj = self.env['hr.contract.holidays']
        for line in self.holidays_employee_ids.search([('apply', '=', True), ('holidays_employee_id', '=', self.id)]):
            leave_allocation_id = leave_allocation_obj.create({
                'name': 'VACACIONES-{}'.format(line.employee_id.name),
                'holiday_status_id': self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id,
                'number_of_days_display': float(line.l10n_mx_holidays),
                'number_of_days': float(line.l10n_mx_holidays),
                'holiday_type': 'employee',
                'employee_id': line.employee_id.id,
                'contract_id': line.contract_id.id,
                'date_from': datetime.now().date().replace(day=1, month=1),
            })
            leave_allocation_id.action_confirm()
            leave_allocation_id.action_validate()
            date_start = datetime.now().date().replace(day=1, month=1)
            holidays_contract_id = holidays_contract_obj.create({
                'holidays_contract_id': line.contract_id.id,
                'date_start': date_start,
                'date_end': date_start + relativedelta(days=line.l10n_mx_holidays),
                'holiday_status_id': self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id,
                'days_assigned': float(line.l10n_mx_holidays),
                'days_enjoyed': 0,
                'days_available': float(line.l10n_mx_holidays),
            })
            line.contract_id.write({'contract_holidays_ids': [(4, holidays_contract_id.id)]})
        self.write({'state': 'get'})
        return {
            'type': 'ir.actions.act_window',
            'name': _('Generate holidays'),
            'res_model': 'generate.holidays.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }


class GenerateHolidaysLineWizard(models.TransientModel):
    _name = 'generate.holidays.line.wizard'
    _description = "Holidays employee line wizard"

    holidays_employee_id = fields.Many2one('generate.holidays.wizard', string='Generate holidays')
    apply = fields.Boolean(default=False, string='Apply')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    contract_id = fields.Many2one('hr.contract', string='Contract')
    department_id = fields.Many2one(related='contract_id.department_id')
    job_id = fields.Many2one(related='contract_id.job_id')
    date_start = fields.Date(related='contract_id.date_start')
    l10n_mx_antiquity = fields.Char(related='contract_id.l10n_mx_antiquity')
    l10n_mx_holidays = fields.Integer(string="Days of holidays", compute='_compute_l10n_mx_holidays', store=True)

    @api.depends('contract_id', 'date_start')
    def _compute_l10n_mx_holidays(self):
        for record in self:
            if record.contract_id.l10n_mx_type_benefit_id and record.date_start:
                antiquity = relativedelta(fields.Date.today(), record.date_start).years
                type_benefit_line_id = record.contract_id.l10n_mx_type_benefit_id.find_rule_by_antiquity(antiquity)
                record.l10n_mx_holidays = type_benefit_line_id.holidays
            else:
                record.l10n_mx_holidays = False
