from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrScholarshipRegistrationWizard(models.TransientModel):
    _name = 'hr.scholarship.registration.wizard'
    _description = 'Hr Scholarship Registration Wizard'

    date_from = fields.Date(
        string='Amortization Date From',
        required=True
    )
    date_to = fields.Date(
        string='Amortization Date To',
        required=True
    )

    @api.constrains('date_to')
    def _check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError(_('Error: invalid date'))

    def action_export_pdf(self):
        scholarship_model = self.env['hr.scholarship.registration.line']

        docs = scholarship_model.search(
            [('amortization_date', '>=', self.date_from), ('amortization_date', '<=', self.date_to)]
        )
        if not docs:
            raise ValidationError(_('No results in the search.'))

        scholarship = [{
                'amortization_date': doc.amortization_date,
                'lote': doc.lote_id.name,
                'number_employee': doc.number_employee,
                'employee_id': doc.employee_id.name,
                'contract_id': doc.contract_id.name,
                'scholarship_id': doc.scholarship_id.name,
                'grade_id': doc.grade_id.grade,
                'qualification': doc.qualification,
                'amount': doc.amount,
                'amount2': doc.amount2,
                'state': doc.state,
                'create_uid': doc.create_uid.login,
            } for doc in docs
        ]
        
        datas = {
            'doc_model': 'hr.scholarship.registration.line',
            'scholarship': scholarship,
        }
        return self.env.ref('erp_l10n_payslip_relatives_scholarship.hr_scholarship_registration_pdf_report').report_action(self, data=datas)

    def action_export_xls(self):
        scholarship_model = self.env['hr.scholarship.registration.line']
        docs = scholarship_model.search(
            [('amortization_date', '>=', self.date_from), ('amortization_date', '<=', self.date_to)]
        )
        if not docs:
            raise ValidationError(_('No results in the search.'))

        datas = {
            'doc_model': 'hr.scholarship.registration.line',
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        return self.env.ref('erp_l10n_payslip_relatives_scholarship.hr_xlsx_report').report_action(self, data=datas)
