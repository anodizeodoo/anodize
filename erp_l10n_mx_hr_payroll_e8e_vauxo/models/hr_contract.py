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
                                   tracking=True, index=True,
                                   string='Type salary', default='fixed')
    history_salary_employee_ids = fields.One2many('l10n.mx.history.salary.employee', 'contract_id', 'MS History', index=True)

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(HrContract, self).create(vals_list)
        for res in res_ids:
            if res.l10n_mx_date_imss:
                history_salary_employee_id = self.env['l10n.mx.history.salary.employee'].sudo().create({
                    'contract_id': res.id,
                    'date': res.l10n_mx_date_imss,
                    'l10n_mx_payroll_daily_salary_new': res.l10n_mx_payroll_daily_salary,
                    'l10n_mx_payroll_integrated_salary_new': res.l10n_mx_payroll_integrated_salary,
                    'state': 'high',
                })
                res.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
        return res_ids

    def write(self, vals):
        res = super(HrContract, self).write(vals)
        if 'state' in vals and vals['state'] in ('close', 'cancel'):
            history_salary_employee_id = self.env['l10n.mx.history.salary.employee'].sudo().create({
                'contract_id': self.id,
                'date': fields.Datetime.now().date(),
                'l10n_mx_payroll_daily_salary_new': self.l10n_mx_payroll_daily_salary,
                'l10n_mx_payroll_integrated_salary_new': self.l10n_mx_payroll_integrated_salary,
                'state': 'low',

            })
            self.history_salary_employee_ids = [(4, history_salary_employee_id.id)]
        if 'state' in vals and vals['state'] == 'open':
            history_salary_employee = self.history_salary_employee_ids.search([], order='date desc', limit=1)
            if history_salary_employee.state == 'low':
                history_salary_employee_id = self.env['l10n.mx.history.salary.employee'].sudo().create({
                    'contract_id': self.id,
                    'date': self.l10n_mx_date_imss,
                    'l10n_mx_payroll_daily_salary_new': self.l10n_mx_payroll_daily_salary,
                    'l10n_mx_payroll_integrated_salary_new': self.l10n_mx_payroll_integrated_salary,
                    'state': 're-entry',

                })
                self.history_salary_employee_ids = [(4, history_salary_employee_id.id)]

        return res

class HrEmployee(models.Model):
    _inherit = "hr.employee"


    #  Payments
    l10n_mx_edi_payment_method_id = fields.Many2one('l10n_mx_edi.payment.method',
                                                    string="Payment Way",
                                                    help="Indicates the way the invoice was/will be paid, where the options could be: "
                                                         "Cash, Nominal Check, Credit Card, etc. Leave empty if unkown and the XML will show 'Unidentified'.",
                                                    default=lambda self: self.env.ref(
                                                        'l10n_mx_edi.payment_method_otros', raise_if_not_found=False))


class HistorySalaryEmployee(models.Model):
    _name = 'l10n.mx.history.salary.employee'
    _description = "MS History"

    date = fields.Date(string='Date', index=True)
    l10n_mx_payroll_daily_salary_new = fields.Float(string='SD New', digits=(16, 2), index=True)
    l10n_mx_payroll_integrated_salary_new = fields.Float(string='SBC New', digits=(16, 2), index=True)
    contract_id = fields.Many2one('hr.contract', string='Contract', index=True)
    state = fields.Selection([("high", "High"), ("modify", "Modify"), ("low", "Low"), ('re-entry', 'Re-entry')], string='State', index=True)
