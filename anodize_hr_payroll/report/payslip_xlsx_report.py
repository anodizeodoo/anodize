# -*- coding: utf-8 -*-

from odoo import models, tools, _
from odoo.exceptions import ValidationError


class PayslipXlsx(models.AbstractModel):
    _name = 'report.anodize_hr_payroll.payslip_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Payslip Report'

    def generate_xlsx_report(self, workbook, data, docs):

        normal_format = workbook.add_format(
            {'bold': 0, 'border': 1, 'align': 'left', 'valign': 'vcenter', 'font': {'size': 10}})
        head_format = workbook.add_format(
            {'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vdistributed', 'font': {'size': 10}})
        format_num = workbook.add_format({'font_size': 10, 'align': 'vright', 'border': 1, 'bold': False, 'num_format': '#,##0.00'})

        name_sheet = "Payslip"
        sheet = workbook.add_worksheet(name_sheet)

        sheet.write(0, 0, tools.ustr(_('Nómina')), head_format)
        sheet.write(0, 1, tools.ustr(_('Empleado')), head_format)
        sheet.write(0, 2, tools.ustr(_('Cuenta')), head_format)
        sheet.write(0, 3, tools.ustr(_('Monto')), head_format)
        # rules = self.env['hr.salary.rule'].search([('struct_id', '=', docs[0].struct_id.id)])
        # y = 4
        # for rule in rules:
        #     sheet.write(0, y, tools.ustr(rule.code), head_format)
        #     y += 1
        x = 1
        for payslip in docs:
            sheet.write(x, 0, tools.ustr(payslip.number), normal_format)
            sheet.write(x, 1, tools.ustr(payslip.employee_id.name), normal_format)
            sheet.write(x, 2, tools.ustr(payslip.employee_id.bank_account_id.acc_number), normal_format)
            sheet.write(x, 3, payslip.net_wage, format_num)
            # y = 4
            # for line in payslip.line_ids:
            #     sheet.write(x, y, line.total, format_num)
            #     y += 1
            x += 1

        sheet.set_column('A:A', 15)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 25)
        sheet.set_column('D:D', 15)
