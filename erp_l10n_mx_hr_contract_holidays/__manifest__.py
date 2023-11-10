# coding: utf-8
{
    "name": "Mexican Contracts Holidays Concepts",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "category": "Human Resources/Payroll",
    "website": "https://www.soltein.net",
    "license": "AGPL-3",
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
        "data/seq_type_considered.xml",
        "data/type_considered_data.xml",
        "data/hr_leave_type_data.xml",
        "data/insurance_branch_data.xml",
        "data/risk_type_data.xml",
        "data/sequel_data.xml",
        "data/disability_control_data.xml",
        # "views/hr_contract_view.xml",
        # "views/ir_sequence_views.xml",
        # "views/res_config_settings_views.xml",
        # "views/table_holidays_views.xml",
        # "views/hr_leave_type_considered_views.xml",
        # "views/hr_leave_type_views.xml",
        # "views/hr_leave_views.xml",
        # "views/insurance_branch_views.xml",
        # "views/risk_type_views.xml",
        # "views/sequel_views.xml",
        # "views/disability_control_views.xml",
        # "views/hr_payslip_views.xml",
        # "views/hr_work_entry_views.xml",
        # "wizard/generate_holidays_views.xml",
        # "wizard/modify_date_imss_views.xml",
        # "wizard/modify_state_contract_views.xml",
    ],
    "installable": True,
}
