# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payroll",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "l10n_mx_edi_extended",
        "hr_payroll_holidays",
        "hr_payroll_account",
    ],
    "demo": [
        "demo/employee_demo.xml",
        "demo/res_users_demo.xml",
        "demo/payroll_cfdi_demo.xml",
        "demo/res_company_demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/3.3/payroll12.xml",
        "data/hr_holidays_data.xml",
        "data/mail_template.xml",
        "data/ir_cron_data.xml",
        "views/hr_payslip_view.xml",
        "views/hr_contract_view.xml",
        "views/hr_employee_views.xml",
        "views/hr_payslip_report.xml",
        "views/hr_salary_rule_views.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_view.xml",
        "data/hr_contract_type_data.xml",
        "data/hr_employee_data.xml",
        "data/payroll_structure_data.xml",
        "data/salary_category_data.xml",
        "data/salary_rule_data.xml",
        "data/salary_rule_finiquito_data.xml",
        "data/salary_rule_christmas_bonus_data.xml",
        "data/salary_rule_liquidacion_data.xml",
        "wizards/payslip_reports_view.xml",
    ],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False
}
