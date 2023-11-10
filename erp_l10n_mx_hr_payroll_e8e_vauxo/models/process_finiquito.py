# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from odoo import api, fields, models, _
from odoo.tools.misc import format_date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class ProcessFiniquito(models.Model):
    _name = "l10n.mx.process.finiquito"
    _description = "Process Finiquito"
    _rec_name = 'contract_id'

    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
    employee_id = fields.Many2one(related='contract_id.employee_id', compute_sudo=True)
    department_id = fields.Many2one(related='contract_id.department_id', compute_sudo=True)
    job_id = fields.Many2one(related='contract_id.job_id', compute_sudo=True)
    date_start = fields.Date(related='contract_id.l10n_mx_date_imss', compute_sudo=True)
    date_end = fields.Date(string='Date End', index=True)
    time_work = fields.Integer(string='Time Work', compute='_compute_time_work', readonly=False)
    l10n_mx_antiquity = fields.Char(related='contract_id.l10n_mx_antiquity', compute_sudo=True)
    wage = fields.Monetary(related='contract_id.wage',
                           currency_field='company_currency_id',
                           compute_sudo=True)
    company_currency_id = fields.Many2one('res.currency',
                                          related='contract_id.company_id.currency_id',
                                          string="Company Currency",
                                          compute_sudo = True,
                                          readonly=True)
    l10n_mx_payroll_daily_salary = fields.Float(related='contract_id.l10n_mx_payroll_daily_salary',
                                                compute_sudo=True)
    l10n_mx_holidays = fields.Integer(string='Days of holidays', compute='_compute_l10n_mx_contract',
                                      readonly=False)
    l10n_mx_vacation_bonus = fields.Integer(string='Vacation cousin (%)',
                                            compute='_compute_l10n_mx_contract', readonly=False)
    l10n_mx_christmas_bonus = fields.Integer(string='Bonus Days',
                                             compute='_compute_l10n_mx_contract', readonly=False)
    line_ids = fields.One2many('l10n.mx.process.finiquito.line', 'finiquito_id', string='Finiquito')
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', index=True)

    @api.depends('date_start', 'date_end')
    def _compute_time_work(self):
        for record in self:
            if record.date_start and record.date_end:
                record.time_work = (record.date_end - record.date_start).days
            else:
                record.time_work = False

    @api.depends('contract_id')
    def _compute_l10n_mx_contract(self):
        for record in self:
            if record.contract_id:
                record.l10n_mx_holidays = record.contract_id.l10n_mx_holidays
                record.l10n_mx_vacation_bonus = record.contract_id.l10n_mx_vacation_bonus
                record.l10n_mx_christmas_bonus = record.contract_id.l10n_mx_christmas_bonus
            else:
                record.l10n_mx_holidays = False
                record.l10n_mx_vacation_bonus = False
                record.l10n_mx_christmas_bonus = False

    def calculate(self):
        self._compute_l10n_mx_contract()
        self._compute_time_work()
        return True

    def generate_payslip(self):
        payslip_obj = self.env['hr.payslip'].sudo()
        struct_type_id = self.env['hr.payroll.structure.type'].search([('is_finiquito', '=', True)], limit=1)
        if struct_type_id:
            struct_id = self.env['hr.payroll.structure'].search([('type_id', '=', struct_type_id.id)])
        else:
            raise ValidationError(_('There is no structure for Finiquito.'))
        line = []
        for finiquito in self.line_ids:
            if finiquito.is_payslip:
                line.append((0, 0, {
                    'name': finiquito.rule_id.name,
                    'code': finiquito.rule_id.code,
                    'salary_rule_id': finiquito.rule_id.id,
                    'amount': finiquito.amount if finiquito.is_amount_payslip else 0,
                }))
        payslip_id = payslip_obj.create({
            'date_from': datetime.now().date().replace(day=1),
            'date_to': datetime.now().date().replace(day=30),
            'name': '{}-{}-{}'.format(_('Salary Slip'), self.employee_id.name, format_date(self.env, datetime.now().date(), date_format="MMMM y", lang_code=self.env.user.lang)),
            'l10n_mx_payment_date': datetime.now().date(),
            'contract_id': self.contract_id.id,
            'employee_id': self.employee_id.id,
            'struct_id': struct_id.id,
            'l10n_mx_payslip_type': struct_id.l10n_mx_payslip_type,
            'l10n_mx_edi_payment_method_id': self.employee_id.l10n_mx_edi_payment_method_id.id,
            'line_ids': line,
        })
        self.payslip_id = payslip_id.id
        return True


class ProcessFiniquitoLine(models.Model):
    _name = "l10n.mx.process.finiquito.line"
    _description = "Process Finiquito Line"

    rule_id = fields.Many2one('hr.salary.rule', string='Rule')
    finiquito_id = fields.Many2one('l10n.mx.process.finiquito', string='Finiquito')
    days = fields.Integer(string='Days')
    is_payslip = fields.Boolean(string='Is Payslip', default=False)
    company_currency_id = fields.Many2one('res.currency',
                                          related='finiquito_id.contract_id.company_id.currency_id',
                                          string="Company Currency",
                                          compute_sudo = True,
                                          readonly=True)
    amount = fields.Monetary(string='Amount', currency_field='company_currency_id')
    is_amount_payslip = fields.Boolean(string='Is Amount Payslip', default=False)



