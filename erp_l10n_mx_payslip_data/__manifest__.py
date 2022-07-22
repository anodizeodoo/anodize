# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Payslip Payslip Base data",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "erp_l10n_mx_payslip_cfdi_base",
    ],
    "data": [
        "data/hr_holidays_data.xml",
        "data/payroll_structure_data.xml",
        "data/salary_category_data.xml",
        "data/salary_rule_data.xml",
        "data/salary_rule_finiquito_data.xml",
        "data/salary_rule_christmas_bonus_data.xml",
        "data/salary_rule_liquidacion_data.xml",
    ],
    "installable": True,
}
