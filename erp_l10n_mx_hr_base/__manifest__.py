# coding: utf-8
{
    "name": "Mexican Employee & Contracts Information",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
    "depends": [
        "hr_contract",
        "erp_hr_employee_sequence",
        "hr_employee_lastnames",
        "l10n_mx_edi_extended",
        "hr_payroll",
        "l10n_mx_edi_extended_40",
    ],
    "demo": [
        "demo/employee_demo.xml",
    ],
    "data": [
        "data/hr_employee_data.xml",
        "data/contract_type_data.xml",
        "data/contract_regime_type_data.xml",
        "data/job_risk_data.xml",
        "data/type_benefit_data.xml",
        "data/schedule_pay_data.xml",
        "data/ir_cron_data.xml",
        "security/ir.model.access.csv",
        "views/hr_contract_view.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_type_views.xml",
        "views/contract_regime_type_views.xml",
        "views/job_risk_views.xml",
        "views/res_config_settings_view.xml",
        "views/res_partner_views.xml",
        "views/type_benefit_views.xml",
        "views/schedule_pay_views.xml",
    ],
    "installable": True,
}
