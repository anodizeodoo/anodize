# -*- coding: utf-8 -*-
{
    'name': 'HR Employee Learning',
    'category': 'Human Resources/Employees',
    'summary': """
        This module allows your to manage employee's training courses""",
    'version': '16.0.1.0.0',
    'author': 'Soltein SA de CV',
    'website': 'https://www.soltein.net',
    'depends': [
        'hr',
        'mail',
    ],
    'data': [
        'security/course_security.xml',
        'security/ir.model.access.csv',
        'views/hr_course_category_views.xml',
        'views/hr_course_views.xml',
        'views/hr_employee_views.xml',
    ],
    "installable": True,
    "license": "AGPL-3",
}