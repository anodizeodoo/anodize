# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class HrRegisterOvertimeLine(models.Model):
    _name = 'hr.register.overtime.line'
    _description = 'Line Register Overtime'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip', index=True)
    number = fields.Char(related='payslip_id.number', string='Payslip', compute_sudo=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
    employee_id = fields.Many2one(related='payslip_id.employee_id', string='Employee', compute_sudo=True)
    daily_salary = fields.Float(related='contract_id.l10n_mx_payroll_daily_salary', compute_sudo=True)
    hours_per_day = fields.Float(related='contract_id.resource_calendar_id.hours_per_day', compute_sudo=True)
    cost_hour = fields.Float(string='Cost Hour', compute='_compute_cost_hour', compute_sudo=True)
    work_hour = fields.Float(string='Work Hour', digits=(16, 2), index=True)
    overtime_type_id = fields.Many2one('hr.type.overtime', string='Type', index=True)
    amount = fields.Float(string="Amount", compute='_compute_amount', compute_sudo=True)
    register_overtime_id = fields.Many2one('hr.register.overtime', string='Register Overtime', ondelete='cascade')
    name = fields.Char(related='register_overtime_id.name', compute_sudo=True)

    @api.depends('daily_salary', 'hours_per_day')
    def _compute_cost_hour(self):
        for record in self:
            if record.daily_salary and record.hours_per_day:
                record.cost_hour = record.daily_salary / record.hours_per_day
            else:
                record.cost_hour = False

    @api.depends('cost_hour', 'work_hour')
    def _compute_amount(self):
        for record in self:
            if record.overtime_type_id.id == self.env.ref('erp_l10n_mx_payslip_overtime.type_overtime_03').id:
                value = 3
            elif record.overtime_type_id.id == self.env.ref('erp_l10n_mx_payslip_overtime.type_overtime_02').id:
                value = 2
            else:
                value = 1
            if record.cost_hour and record.work_hour:
                record.amount = record.work_hour * record.cost_hour * value
            else:
                record.amount = 0


class HrRegisterOvertime(models.Model):
    _name = 'hr.register.overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Register Overtime'

    name = fields.Char('Name', index=True)
    date_from = fields.Date(string='From', default=lambda self: fields.Date.to_string(date.today().replace(day=1)), index=True)
    date_to = fields.Date(string='To', default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()), index=True)
    state = fields.Selection([("draft", "Draft"), ("load", "Load"), ("validate", "Validate")], string='State', default='draft', index=True)
    overtime_type_id = fields.Many2one('hr.type.overtime', string='Type', index=True)
    register_overtime_line_ids = fields.One2many('hr.register.overtime.line', 'register_overtime_id', string='Register Line Extra hours')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('hr.overtime.seq')
        return super(HrRegisterOvertime, self).create(vals)

    def load_contracts(self):
        query = """
                    INSERT INTO hr_register_overtime_line (payslip_id, contract_id, register_overtime_id, overtime_type_id)
                        WITH cte AS 
                            (SELECT id FROM hr_contract WHERE state='open' AND is_extra_hours=true)
                            SELECT hp.id, hp.contract_id, %s, %s FROM hr_payslip AS hp                                
                                INNER JOIN cte ON cte.id = hp.contract_id
                                WHERE hp.state='draft' AND hp.date_from >= %s AND hp.date_to <= %s
                """
        self._cr.execute(query, (self.id, self.overtime_type_id.id, self.date_from, self.date_to))
        self.write({'state': 'load'})
        return True

    def button_draft(self):
        self.write({'state': 'draft'})
        self.register_overtime_line_ids.unlink()
        return True

    def button_validate(self):
        self.register_overtime_line_ids.search([('work_hour', '=', False), ('register_overtime_id', '=', self.id)]).unlink()
        self.write({'state': 'validate'})
        return True

    def unlink(self):
        for record in self:
            if record.state == 'validate':
                raise ValidationError(_("The Extra Hours is validate, therefore you cannot delete it."))
        return super(HrRegisterOvertime, self).unlink()
