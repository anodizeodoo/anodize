# -*- coding: utf-8 -*-
{
    'name': "Hr Category Contract",
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'website': "https://www.soltein.net",
    'author': "Viixoo & Soltain",
    'summary': """Hr Category Contract""",
    'depends': [
        'erp_l10n_mx_hr_payroll_e8e_vauxo',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_category_views.xml',
        'views/hr_contract_views.xml',
        'views/l10n_mx_modify_salary_views.xml',
        'views/hr_employee_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            "erp_l10n_mx_hr_contract_category/static/src/js/smile_confirmation.js",
        ]
    },
}
