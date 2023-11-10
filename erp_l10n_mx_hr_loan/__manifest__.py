# coding: utf-8
{
    "name": "Mexican Employee Loans",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Human Resources/Payroll",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
    "depends": [
        "erp_l10n_mx_hr_base",
    ],
    "data": [
        "data/loan_type_data.xml",
        "security/ir.model.access.csv",
        "views/hr_contract_views.xml",
        "views/loan_type_views.xml",
        "views/hr_salary_rule_views.xml",
    ],
    "installable": True,
}
