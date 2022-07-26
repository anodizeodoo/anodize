# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payslip CFDI Base",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "erp_l10n_mx_hr_base",
        "erp_l10n_mx_hr_contract_holidays",
        "erp_l10n_mx_hr_loan",
        "erp_l10n_mx_payslip_inability",
        "erp_l10n_mx_payslip_overtime",
        "hr_payroll_account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/3.3/payroll12.xml",
        "data/4.0/payroll12.xml",
        "data/table_isr_data.xml",
        "data/sat_keys_data.xml",
        "views/res_config_settings_views.xml",
        "views/hr_salary_rule_views.xml",
        "views/hr_contract_view.xml",
        "views/hr_payslip_view.xml",
        "views/table_isr_views.xml",
        "views/sat_keys_views.xml",
    ],
    "installable": True,
}
