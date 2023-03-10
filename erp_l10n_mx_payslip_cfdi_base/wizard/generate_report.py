# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools


class GenerateReportWizard(models.TransientModel):
    _name = 'generate.report.wizard'
    _description = 'Generate report wizard'

    def _get_department_start_id(self):
        departments = self.env['hr.department'].search([], order='id asc')
        if departments:
            return departments[0].id
        else:
            False

    def _get_department_end_id(self):
        departments = self.env['hr.department'].search([], order='id desc')
        if departments:
            return departments[0].id
        else:
            False

    def _get_employee_start_id(self):
        employees = self.env['hr.employee'].search([], order='id asc')
        if employees:
            return employees[0].id
        else:
            False

    def _get_employee_end_id(self):
        employees = self.env['hr.employee'].search([], order='id desc')
        if employees:
            return employees[0].id
        else:
            False

    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    employer_registration_ids = fields.Many2many('l10n_mx_payroll.employer.registration', 'employer_registration_report_rel', string='Employer Registry')
    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure')
    department_start_id = fields.Many2one('hr.department', string='Department start', default=_get_department_start_id)
    department_end_id = fields.Many2one('hr.department', string='Department end', default=_get_department_end_id)
    employee_start_id = fields.Many2one('hr.employee', string='Employee start', default=_get_employee_start_id)
    employee_end_id = fields.Many2one('hr.employee', string='Employee end', default=_get_employee_end_id)

    state = fields.Selection([('choose', 'choose'), ('get', 'get')], default='choose')
    txt_filename = fields.Char('filename', readonly=True)
    txt_binary = fields.Binary('file', readonly=True)

    @api.depends('department_start_id', 'department_end_id')
    def list_range_department(self):
        if self.department_start_id.id > self.department_end_id.id:
            department_start_id = self.department_end_id
            department_end_id = self.department_start_id
        else:
            department_start_id = self.department_start_id
            department_end_id = self.department_end_id
        return self.env['hr.department'].search(
            [('id', '>=', department_start_id.id), ('id', '<=', department_end_id.id)], order='id asc').ids

    @api.depends('employee_start_id', 'employee_end_id')
    def list_range_employee(self):
        if self.employee_start_id.id > self.employee_end_id.id:
            employee_start_id = self.employee_end_id
            employee_end_id = self.employee_start_id
        else:
            employee_start_id = self.employee_start_id
            employee_end_id = self.employee_end_id
        return self.env['hr.employee'].search(
            [('id', '>=', employee_start_id.id), ('id', '<=', employee_end_id.id)], order='id asc').ids

    def generate_file(self):

        domain = [('employee_id', 'in', self.list_range_employee()),
                    ('employee_id.department_id', 'in', self.list_range_department()),
                    ('date_from', '>=', self.date_start),
                    ('date_to', '<=', self.date_end),
                    ('struct_id', '=', self.struct_id.id)]

        group_payslips = self.env['hr.payslip'].search(domain, order='employee_id asc')

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet("Reporte de Nomina General")

        cell_bold_left = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'left', 'font_size': 9})
        cell_left = workbook.add_format({'text_wrap': 1, 'align': 'left', 'font_size': 9})
        cell_right = workbook.add_format({'text_wrap': 1, 'align': 'right', 'font_size': 9})
        cell_bold_right = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'right', 'font_size': 9})
        cell_format_line = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'vcenter', 'font_size': 11})
        merge_format_border_bottom = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'left', 'bottom': 1, 'font_size': 9})
        merge_format_border_top = workbook.add_format({'bold': 1, 'text_wrap': 1, 'align': 'left', 'top': 1, 'font_size': 9})

        worksheet.set_column('A1:B1', 15)
        worksheet.set_column('E1:F1', 15)

        image_data = BytesIO(base64.b64decode(tools.image_process(self.env.company.logo, size=(0, 180))))
        worksheet.insert_image('A1:B2', "Logo.png", {'image_data': image_data, 'x_scale': 0.34, 'y_scale': 0.34, 'object_position': 1})
        worksheet.merge_range('A1:B2', '', cell_bold_left)
        worksheet.merge_range('A3:B3', 'Reg Pat IMSS: {}'.format(", ".join(rp.name for rp in self.employer_registration_ids)), cell_bold_left)
        worksheet.merge_range('A4:B4', 'RFC: {}'.format(self.env.company.vat), cell_bold_left)
        worksheet.merge_range('C1:G4', "Lista de Raya del {} al {}".format(self.date_start, self.date_end), cell_format_line)
        worksheet.merge_range('H1:I4', "Fecha: {} \n Hora: {}".format(datetime.now().date().strftime("%d/%m/%Y"), datetime.now().strftime("%H:%M:%S")), cell_bold_right)
        worksheet.merge_range('A5:I5', " ", merge_format_border_bottom)
        worksheet.merge_range('A6:B6', "Percepción", merge_format_border_bottom)
        worksheet.write_string('C6', 'Valor', merge_format_border_bottom)
        worksheet.write_string('D6', 'Importe', merge_format_border_bottom)
        worksheet.merge_range('E6:G6', "Deduccción", merge_format_border_bottom)
        worksheet.write_string('H6', 'Valor', merge_format_border_bottom)
        worksheet.write_string('I6', 'Importe', merge_format_border_bottom)

        rowcont = 7
        for department in self.list_range_department():
            payslips = group_payslips.filtered(lambda p: p.employee_id.department_id.id == department)
            lines_dict = {'perception': {}, 'deduction': {}}
            perceptions, deductions = [], []
            total_net_payment = 0.00
            for payslip in payslips:
                worksheet.merge_range('A{}:B{}'.format(rowcont, rowcont), payslip.employee_id.registration_number, cell_bold_left)
                worksheet.merge_range('C{}:I{}'.format(rowcont, rowcont), payslip.employee_id.name, cell_bold_left)
                rowcont += 1
                worksheet.merge_range('A{}:D{}'.format(rowcont, rowcont), 'RFC: {}'.format(payslip.employee_id.l10n_mx_edi_rfc), cell_left)
                worksheet.merge_range('E{}:I{}'.format(rowcont, rowcont), 'Afiliación IMSS: {}'.format(payslip.employee_id.ssnid), cell_left)
                rowcont += 1
                worksheet.merge_range('A{}:B{}'.format(rowcont, rowcont), 'Fecha Ingr: {}'.format(payslip.contract_id.date_start), cell_left)
                worksheet.merge_range('C{}:D{}'.format(rowcont, rowcont), 'Sal. diario: {}'.format(payslip.contract_id.l10n_mx_payroll_daily_salary), cell_left)
                worksheet.write('E{}'.format(rowcont), 'S.D.I: {}'.format(payslip.contract_id.l10n_mx_payroll_integrated_salary), cell_left)
                worksheet.merge_range('F{}:G{}'.format(rowcont, rowcont), 'S.B.C: {}'.format(payslip.contract_id.l10n_mx_sdi_total), cell_left)
                type_salary = dict(payslip.contract_id._fields['type_salary'].selection)[payslip.contract_id.type_salary]
                type_salary_i18n = self.env['ir.translation'].sudo().search([('type', '=', 'model'), ('src', '=', type_salary), ('module', '=', 'erp_l10n_mx_hr_payroll_e8e_vauxo'), ('lang', '=', self.env.user.lang)])
                worksheet.merge_range('H{}:I{}'.format(rowcont, rowcont), type_salary_i18n[0].value if type_salary_i18n and type_salary_i18n[0].value else '', cell_left)
                rowcont += 1
                day_payment = sum(payslip.worked_days_line_ids.mapped('number_of_days'))
                worksheet.merge_range('A{}:B{}'.format(rowcont, rowcont), 'Días pagados: {}'.format(day_payment), cell_left)
                worksheet.merge_range('C{}:D{}'.format(rowcont, rowcont), 'Tot. Hrs trab: {}'.format(sum(payslip.worked_days_line_ids.mapped('number_of_hours'))), cell_left)
                worksheet.write('E{}'.format(rowcont), 'Hrs día: {}'.format(payslip.employee_id.resource_calendar_id.hours_per_day), cell_left)
                worksheet.write_string('F{}'.format(rowcont), 'Hrs extras: {}'.format(sum(payslip.l10n_mx_overtime_line_ids.mapped('hours'))), cell_left)
                worksheet.merge_range('G{}:I{}'.format(rowcont, rowcont), 'CURP: {}'.format(payslip.employee_id.l10n_mx_edi_curp), cell_left)
                rowcont += 1
                perception_rowcont = rowcont
                total_perception = 0.00
                for perception in payslip.get_cfdi_perceptions_data()['perceptions']:
                    perception_name = '{} {}'.format(perception.code, perception.name)
                    worksheet.merge_range('A{}:B{}'.format(perception_rowcont, perception_rowcont), perception_name, cell_left)
                    worksheet.write('C{}'.format(perception_rowcont), day_payment, cell_left)
                    worksheet.write('D{}'.format(perception_rowcont), perception.total, cell_right)
                    total_perception += perception.total
                    perception_rowcont += 1

                    if perception.code not in lines_dict['perception']:
                        perceptions.append(perception.code)
                        lines_dict['perception'][perception.code] = {
                            'name': perception_name,
                            'amount': perception.total,
                        }
                    else:
                        lines_dict['perception'][perception.code]['amount'] += perception.total

                deduction_rowcont = rowcont
                total_deduction = 0.00
                for deduction in payslip.get_cfdi_deductions_data()['deductions']:
                    deduction_name = '{} {}'.format(deduction.code, deduction.name)
                    worksheet.merge_range('E{}:H{}'.format(deduction_rowcont, deduction_rowcont), deduction_name, cell_left)
                    worksheet.write('I{}'.format(deduction_rowcont), deduction.total, cell_right)
                    total_deduction += deduction.total
                    deduction_rowcont += 1

                    if deduction.code not in lines_dict['deduction']:
                        deductions.append(deduction.code)
                        lines_dict['deduction'][deduction.code] = {
                            'name': deduction_name,
                            'amount': deduction.total,
                        }
                    else:
                        lines_dict['deduction'][deduction.code]['amount'] += deduction.total

                rowcont = perception_rowcont if perception_rowcont > deduction_rowcont else deduction_rowcont
                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Total Percepciones', cell_left)
                worksheet.write('D{}'.format(rowcont), total_perception, cell_right)
                worksheet.merge_range('E{}:H{}'.format(rowcont, rowcont), 'Total Deducciones', cell_left)
                worksheet.write('I{}'.format(rowcont), total_deduction, cell_right)
                rowcont += 1
                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Neto a Pagar', cell_bold_left)
                net_payment = total_perception-abs(total_deduction)
                total_net_payment += net_payment
                worksheet.write('D{}'.format(rowcont), net_payment, cell_bold_right)
                rowcont += 1
            if payslips:
                worksheet.merge_range('A{}:I{}'.format(rowcont, rowcont), 'Total Departamento', merge_format_border_top)
                rowcont += 1
                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Percepción', merge_format_border_bottom)
                worksheet.write('D{}'.format(rowcont, rowcont), 'Importe', merge_format_border_bottom)
                worksheet.merge_range('E{}:H{}'.format(rowcont, rowcont), 'Deducción', merge_format_border_bottom)
                worksheet.write('I{}'.format(rowcont, rowcont), 'Importe', merge_format_border_bottom)
                rowcont += 1

                line_perception_rowcont = rowcont
                total_line_perception = 0.00
                for line_perception in perceptions:
                    worksheet.merge_range('A{}:C{}'.format(line_perception_rowcont, line_perception_rowcont), lines_dict['perception'][line_perception]['name'], cell_left)
                    worksheet.write('D{}'.format(line_perception_rowcont, line_perception_rowcont), lines_dict['perception'][line_perception]['amount'], cell_right)
                    line_perception_rowcont += 1
                    total_line_perception += lines_dict['perception'][line_perception]['amount']

                line_deduction_rowcont = rowcont
                total_line_deduction = 0.00
                for line_deduction in deductions:
                    worksheet.merge_range('E{}:H{}'.format(line_deduction_rowcont, line_deduction_rowcont), lines_dict['deduction'][line_deduction]['name'], cell_left)
                    worksheet.write('I{}'.format(line_deduction_rowcont, line_deduction_rowcont), lines_dict['deduction'][line_deduction]['amount'], cell_right)
                    line_deduction_rowcont += 1
                    total_line_deduction += lines_dict['deduction'][line_deduction]['amount']

                rowcont = line_perception_rowcont if line_perception_rowcont > line_deduction_rowcont else line_deduction_rowcont
                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Total Percepciones', cell_left)
                worksheet.write('D{}'.format(rowcont, rowcont), total_line_perception, cell_right)
                worksheet.merge_range('E{}:H{}'.format(rowcont, rowcont), 'Total Deducciones', cell_left)
                worksheet.write('I{}'.format(rowcont, rowcont), total_line_deduction, cell_right)
                rowcont += 1

                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Neto del departamento', cell_left)
                worksheet.write('D{}'.format(rowcont, rowcont), total_net_payment, cell_right)
                rowcont += 1

                worksheet.merge_range('A{}:C{}'.format(rowcont, rowcont), 'Total de empleados', cell_left)
                worksheet.write('D{}'.format(rowcont, rowcont), len(payslips), cell_right)
                rowcont += 1

                worksheet.merge_range('A{}:I{}'.format(rowcont, rowcont), " ", merge_format_border_bottom)
                rowcont += 1

        workbook.close()
        output.seek(0)

        self.write({
            'state': 'get',
            'txt_binary': base64.b64encode(output.getvalue()),
            'txt_filename': 'Reporte de Nomina General.xlsx',
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('General Payroll Report'),
            'res_model': 'generate.report.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new'
        }
