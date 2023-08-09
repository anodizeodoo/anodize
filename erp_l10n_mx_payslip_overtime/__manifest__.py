# coding: utf-8
{
    "name": "Mexican Payslip Extra Hours",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
    "depends": [
        "erp_l10n_mx_hr_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/type_overtime_data.xml",
        "data/seq_hr_overtime.xml",
        "views/hr_payslip_view.xml",
        "views/res_config_settings_views.xml",
        "views/type_overtime_views.xml",
        "views/hr_contract_views.xml",
        "views/register_overtime_views.xml",
        "views/hr_overtime_menu_views.xml",

    ],
    "installable": True,
}
