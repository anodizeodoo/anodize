# coding: utf-8
{
    "name": "Mexican Payslip CFDI",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
    "depends": [
        "erp_l10n_mx_payslip_data",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/cron.xml",
        "data/increment_type_data.xml",
        "data/template_data.xml",
        "views/hr_payslip_view.xml",
        "views/hr_payslip_sat_report.xml",
        "views/hr_payslip_receipt_nonfiscal_report.xml",
        "views/hr_payslip_other_report.xml",
        "views/hr_payroll_reports.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_view.xml",
        "views/res_partner_views.xml",
        "views/increment_type_views.xml",
        "views/modify_salary_views.xml",
        "views/employee_ptu_views.xml",
        "views/process_finiquito_views.xml",
        "views/hr_salary_rule_views.xml",
        "wizard/reason_cancelation_sat_view.xml",
        "wizard/generate_calculation_ptu_views.xml",
    ],
    "installable": True,
}
