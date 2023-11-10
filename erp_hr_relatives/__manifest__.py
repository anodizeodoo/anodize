# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Relatives',
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'website': 'https://www.soltein.net',
    'author': 'Soltein SA de CV',
    'summary': 'Allows storing information about employee family',
    'depends': [
        'hr'
    ],
    'external_dependencies': {
        'python': [
            'dateutil',
        ],
    },
    'data': [
        'data/data_relative_relation.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_employee_relative_views.xml',
        'views/hr_employee.xml',
        'views/hr_employee_relative.xml',
        'views/hr_employee_relative_professions.xml',
        'views/mx_hr_menus.xml',
    ],
    'installable': True,
    "license": "AGPL-3",
}