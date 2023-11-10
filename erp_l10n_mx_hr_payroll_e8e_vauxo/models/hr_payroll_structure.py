# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    template_id = fields.Many2one('mail.template', string='Reporte Envio E-mail')

    @api.model
    def default_get(self, fields):
        res = super(HrPayrollStructure, self).default_get(fields)
        company = self.env.user.company_id
        if company.l10n_mx_payroll_receipt_format:
            if company.l10n_mx_payroll_receipt_format == 'sat_receipt':
                res['report_id'] = self.env.ref('hr_payroll.action_report_payslip').id
            elif company.l10n_mx_payroll_receipt_format == 'other_receipt':
                res['report_id'] = self.env.ref('erp_l10n_mx_hr_payroll_e8e_vauxo.action_report_payslip_other').id
        return res
