# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payslip CFDI",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "erp_l10n_mx_payslip_data",
        "l10n_mx_edi_extended",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "views/hr_payslip_view.xml",
        "views/hr_payslip_sat_report.xml",
        "views/hr_payroll_reports.xml",
        "views/hr_payslip_other_report.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_view.xml",
        "views/res_partner_views.xml",
        "wizard/reason_cancelation_sat_view.xml",
    ],
    "installable": True,
}
