# coding: utf-8
{
    "name": "Mexican Payslip CFDI Base",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Human Resources/Payroll",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
    "depends": [
        "erp_l10n_mx_hr_contract_holidays",
        "erp_l10n_mx_hr_loan",
        "erp_l10n_mx_payslip_inability",
        "erp_l10n_mx_payslip_overtime",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/3.3/payroll12.xml",
        "data/3.3/payroll12_not_curp.xml",
        "data/4.0/payroll12.xml",
        "data/4.0/payroll12_not_curp.xml",
        "data/table_isr_data.xml",
        "data/table_imss_data.xml",
        "data/sat_keys_data.xml",
        "data/schedule_pay_data.xml",
        "data/report_classifier_data.xml",
        "views/res_config_settings_views.xml",
        "views/hr_salary_rule_views.xml",
        "views/hr_contract_view.xml",
        "views/hr_payslip_view.xml",
        "views/table_isr_views.xml",
        "views/table_imss_views.xml",
        "views/sat_keys_views.xml",
        "views/table_minimum_wage_views.xml",
        "views/table_umas_views.xml",
        "views/table_umi_views.xml",
        "views/table_net_adjustments_views.xml",
        "views/schedule_pay_views.xml",
        "views/report_classifier_views.xml",
        "wizard/generate_report_views.xml",
        "reports/receipt_printing_report_pdf.xml",
    ],
    "installable": True,
}
