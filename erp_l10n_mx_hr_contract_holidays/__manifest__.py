# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "Mexican Contracts Holidays Concepts",
    "version": "14.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Localization",
    "website": "https://www.soltein.net",
    "depends": [
        "hr_holidays",
        "hr_work_entry",
        "hr_work_entry_contract",
        "erp_l10n_mx_hr_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/table_holidays_data.xml",
        "data/hr_contract_sequence.xml",
        "views/hr_contract_view.xml",
        "views/ir_sequence_views.xml",
        "views/res_config_settings_views.xml",
        "views/table_holidays_views.xml",
    ],
    "installable": True,
}
