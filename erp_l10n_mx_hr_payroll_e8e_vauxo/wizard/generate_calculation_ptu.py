# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class GenerateReportWizard(models.TransientModel):
    _name = 'generate.calculation.ptu.wizard'
    _description = 'Generate Calculation PTU wizard'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year, datetime.now().year - 5, -1)]

    amount = fields.Float(string='Amount to Distribute')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    day_year = fields.Integer(string='Days years')
    is_accumulated = fields.Boolean(string='Accumulated from the previous fiscal year', default=False)
    is_discount_incidents = fields.Boolean(string='Discount incidents', default=False)
    is_ptu = fields.Boolean(string='Bump into PTU', default=True)
    days = fields.Integer(string='Days')
    salary = fields.Selection([('daily', 'Daily salary'), ('integrated', 'Daily salary integrated')], default='daily', string='Salary')
    date_year = fields.Selection(selection=_get_years, string='Year', default=lambda s: str(datetime.today().year - 1))
    date_from = fields.Date(string='Date from', compute='_compute_date')
    date_to = fields.Date(string='Date to', compute='_compute_date')

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.depends('date_year')
    def _compute_date(self):
        for record in self:
            if record.date_year:
                record.date_from = datetime(int(record.date_year), 1, 1)
                record.date_to = datetime(int(record.date_year), 12, 31)
            else:
                record.date_from = False
                record.date_to = False

    def generate(self):
        employee_ptu_obj = self.env['l10n.mx.employee.ptu'].sudo()
        contract_obj = self.env['hr.contract'].sudo()
        for employee in self.env['hr.employee'].search([]):
            domain = [('employee_id', '=', employee.id),
                      ('date_from', '>=', self.date_from),
                      ('date_to', '<=', self.date_to),
                      ('struct_id', '=', self.struct_id.id),]
            payslips = self.env['hr.payslip'].sudo().search(domain)
            number_of_days = sum(payslips.worked_days_line_ids.mapped('number_of_days'))
            salary_accrued = sum(pay.get_cfdi_perceptions_data()['total_perceptions'] for pay in payslips)
            contract_id = contract_obj.search([('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)
            employee_ptu_obj.create({
                'employee_id': employee.id,
                'struct_id': self.struct_id.id,
                'type': 'S' if employee.l10n_mx_edi_syndicated else 'C',
                'l10n_mx_payroll_contract_type_id': contract_id.l10n_mx_payroll_contract_type_id.id,
                'number_of_days': number_of_days,
                'salary_accrued': salary_accrued,
                'salary': contract_id.l10n_mx_payroll_daily_salary,
                'salary3_month': contract_id.l10n_mx_payroll_daily_salary * self.days,
                'date_year': self.date_year,
            })
        action = self.env["ir.actions.act_window"]._for_xml_id("erp_l10n_mx_hr_payroll_e8e_vauxo.employee_ptu_action")
        return action




    # def generate_file(self):
    #
    #     output = BytesIO()
    #     workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    #     worksheet = workbook.add_worksheet("Reporte de Nomina General")
    #
    #
    #     workbook.close()
    #     output.seek(0)
    #
    #     self.write({
    #         'state': 'get',
    #         'txt_binary': base64.b64encode(output.getvalue()),
    #         'txt_filename': 'Reporte de Nomina General.xlsx',
    #     })
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': _('Calculation PTU'),
    #         'res_model': 'generate.calculation.ptu.wizard',
    #         'view_mode': 'form',
    #         'res_id': self.id,
    #         'target': 'new'
    #     }

