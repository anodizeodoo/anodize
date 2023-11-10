# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Medical ID',
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'summary': 'Allows storing information about employee health',
    'website': 'https://www.soltein.net',
    'author': 'Soltein SA de CV',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data_health_condition_type.xml',
        'data/data_health_condition_severity.xml',
        'data/data_blood_type.xml',
        'views/hr_employee.xml',
        'views/hr_employee_blood_type_view.xml',
        'views/hr_employee_health_condition_severity_views.xml',
        'views/hr_employee_health_condition_type_view.xml',
        'views/hr_employee_health_condition_views.xml',
    ],
    'installable': True,
    "license": "AGPL-3",
}