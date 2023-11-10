# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import datetime
from odoo import fields, models, api
from odoo.exceptions import ValidationError, UserError


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _get_default_considered_id(self):
        considered_3 = False
        try:
            considered_3 = self.env.ref('erp_l10n_mx_hr_contract_holidays.type_considered_3').id
        except Exception as e:
            pass
        return considered_3

    type = fields.Selection([('holidays', 'Holidays'), ('disabilities', 'Disabilities')], string='Type')
    folio = fields.Char(string='Folio', index=True)
    insurance_branch_id = fields.Many2one('l10n.mx.insurance.branch', string='Insurance branch', index=True)
    is_work_risk = fields.Boolean(related='insurance_branch_id.is_work_risk', compute_sudo=True)
    risk_type_id = fields.Many2one('l10n.mx.risk.type', string='Risk type', index=True)
    inability = fields.Float(string='% Inability', digits=(12, 2), index=True)
    sequel_id = fields.Many2one('l10n.mx.sequel', string='Sequel', index=True)
    disability_control_id = fields.Many2one('l10n.mx.disability.control', string='Disability Control', index=True)
    considered_id = fields.Many2one('hr.leave.type.considered', string='It is considered', default=_get_default_considered_id)
    is_vacation = fields.Boolean(string='Vacation')
    is_vacation_bonus = fields.Boolean(string='Vacation bonus')
    amount = fields.Float(string='Amount', digits=(12, 2), index=True)
    inability_date_from = fields.Date('Inability Start Date')
    inability_date_to = fields.Date('Inability End Date')

    def _domain_allocation_holidays(self):
        return [('holiday_status_id', '=', self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id)]

    allocation_id = fields.Many2one('hr.leave.allocation', string='Assignment', domain=_domain_allocation_holidays)

    @api.onchange('considered_id')
    def _onchange_considered_id(self):
        self.holiday_status_id = False
        return {'domain': {'holiday_status_id': [('considered_id', '=', self.considered_id.id)]}}

    @api.onchange('type')
    def _onchange_type(self):
        if self.type == 'disabilities':
            return {'domain': {'holiday_status_id': [('considered_id', '=', self.env.ref('erp_l10n_mx_hr_contract_holidays.type_considered_2').id)]}}
        else:
            return {'domain': {'holiday_status_id': []}}

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        self.insurance_branch_id = False
        if self.holiday_status_id.id == self.env.ref('erp_l10n_mx_payslip_data.mexican_riesgo_de_trabajo').id:
            return {'domain': {'insurance_branch_id': [('id', '=', self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_1').id)]}}
        else:
            return {'domain': {'insurance_branch_id': [('id', '!=', self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_1').id)]}}

    @api.onchange('allocation_id')
    def _onchange_allocation_id(self):
        if self.allocation_id:
            self.employee_id = self.allocation_id.employee_id.id
            self.number_of_days = self.allocation_id.number_of_days_display
            self.holiday_status_id = self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id

    @api.constrains('insurance_branch_id', 'number_of_days')
    def check_insurance_branch_id(self):
        if self.insurance_branch_id.id == self.env.ref('erp_l10n_mx_hr_contract_holidays.insurance_branch_6').id:
            if self.number_of_days > 28 or self.request_date_from < datetime.date(month=6, year=2019, day=4):
                raise UserError('La duración no puede ser mayor que 28 o la fecha de inicio no ser anterior al 4 de junio de 2019.')

    def action_approve(self):
        super(HolidaysRequest, self).action_approve()
        if self.type == 'holidays':
            holidays_contract_obj = self.env['hr.contract.holidays'].sudo()
            for record in self:
                contract_id = record.allocation_id.contract_id
                holidays_contract_id = holidays_contract_obj.search([('hr_leave_id', '=', record.id)])
                if not holidays_contract_id:
                    holidays_contract_id = holidays_contract_obj.create({
                        'holidays_contract_id': contract_id.id,
                        'date_start': record.request_date_from,
                        'date_end': record.request_date_to,
                        'holiday_status_id': self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id,
                        'days_assigned': record.allocation_id.number_of_days_display,
                        'days_enjoyed': record.number_of_days,
                        'days_available': record.allocation_id.number_of_days_display - record.number_of_days,
                        'hr_leave_id': record.id,
                    })
                    days_enjoyed = sum(contract_id.contract_holidays_ids.mapped('days_enjoyed'))
                    holidays_contract_id.write(
                        {'days_available': record.allocation_id.number_of_days_display - days_enjoyed})
                    contract_id.write({'contract_holidays_ids': [(4, holidays_contract_id.id)]})
                else:
                    days_enjoyed = sum(contract_id.contract_holidays_ids.mapped('days_enjoyed')) + record.number_of_days
                    holidays_contract_id.write({
                        'days_enjoyed': record.number_of_days,
                        'days_available': record.allocation_id.number_of_days_display - days_enjoyed
                    })


    def action_refuse(self):
        super(HolidaysRequest, self).action_refuse()
        if self.type == 'holidays':
            holidays_contract_obj = self.env['hr.contract.holidays'].sudo()
            for record in self:
                holidays_contract_id = holidays_contract_obj.search([('hr_leave_id', '=', record.id)])
                if holidays_contract_id:
                    days_available = holidays_contract_id.days_available + holidays_contract_id.days_enjoyed
                    holidays_contract_id.write({
                        'days_enjoyed': 0,
                        'days_available': days_available,
                    })

    @api.model_create_multi
    def create(self, vals_list):
        if self._context.get('from_holidays'):
            for values in vals_list:
                values.update({'holiday_status_id': self.env.ref('erp_l10n_mx_hr_contract_holidays.leave_type_07').id})
        return super(HolidaysRequest, self).create(vals_list)
