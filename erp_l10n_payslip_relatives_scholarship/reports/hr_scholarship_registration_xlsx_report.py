from odoo import fields, models, api


class ScholarshipReport(models.AbstractModel):
    _name = 'report.erp_l10n_payslip_relatives_scholarship.hr_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objs=None):
        # Local variables
        col = 0
        row = 0
        registrationModel = self.env['hr.scholarship.registration.line']

        # Formats
        head_format1 = workbook.add_format({'bold': 1, 'border': 0, 'align': 'center',
                                            'valign': 'vdistributed', 'font_size': 10, 'bg_color': '#FBBA00'})

        sheet = workbook.add_worksheet('Report Scholarship')
        sheet.write(row, col, 'Fecha de Amortización', head_format1)
        col += 1
        sheet.write(row, col, 'Lote', head_format1)
        col += 1
        sheet.write(row, col, '#Empleado', head_format1)
        col += 1
        sheet.write(row, col, 'Empleado', head_format1)
        col += 1
        sheet.write(row, col, 'Contracto', head_format1)
        col += 1
        sheet.write(row, col, 'Becado', head_format1)
        col += 1
        sheet.write(row, col, 'Grado', head_format1)
        col += 1
        sheet.write(row, col, 'Calificación', head_format1)
        col += 1
        sheet.write(row, col, 'Importe', head_format1)
        col += 1
        sheet.write(row, col, 'Importe2', head_format1)
        col += 1
        sheet.write(row, col, 'Estado', head_format1)
        col += 1
        sheet.write(row, col, 'Usuario', head_format1)
        col = 0
        row = 1

        docs = registrationModel.search(
            [('amortization_date', '>=', data['date_from']),
             ('amortization_date', '<=', data['date_to'])]
        )

        for registration_line in docs:
            sheet.write(row, col, str(registration_line.amortization_date))
            col += 1
            sheet.write(row, col, str(registration_line.lote_id.name))
            col += 1
            sheet.write(row, col, str(registration_line.number_employee))
            col += 1
            sheet.write(row, col, str(registration_line.employee_id.name))
            col += 1
            sheet.write(row, col, str(registration_line.contract_id.name))
            col += 1
            sheet.write(row, col, str(registration_line.scholarship_id.name))
            col += 1
            sheet.write(row, col, str(registration_line.grade_id.grade))
            col += 1
            sheet.write(row, col, str(registration_line.qualification))
            col += 1
            sheet.write(row, col, str(registration_line.amount))
            col += 1
            sheet.write(row, col, str(registration_line.amount2))
            col += 1
            sheet.write(row, col, str(registration_line.state))
            col += 1
            sheet.write(row, col, str(registration_line.create_uid.login))
            row += 1
            col = 0
