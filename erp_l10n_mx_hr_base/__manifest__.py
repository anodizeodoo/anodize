# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Employee & Contracts Information",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "hr_contract",
        "hr_employee_lastnames",
        "l10n_mx_edi_extended",
        "l10n_mx_edi_extended_40",
    ],
    "demo": [
        "demo/employee_demo.xml",
    ],
    "data": [
        "data/hr_employee_data.xml",
        "data/contract_type_data.xml",
        "data/contract_regime_type_data.xml",
        "security/ir.model.access.csv",
        "views/hr_contract_view.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_type_views.xml",
        "views/contract_regime_type_views.xml",
        "views/res_config_settings_view.xml",
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
