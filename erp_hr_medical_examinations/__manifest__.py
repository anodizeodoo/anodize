# -*- coding: utf-8 -*-
{
    'name': 'Hr Employee Medical Examinations',
    'category': 'Human Resources/Employees',
    'summary': """
        Adds information about employee's medical examinations""",
    'version': '16.0.1.0.0',
    'author': 'Soltein SA de CV',
    'website': 'https://www.soltein.net',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_employee_medical_examination_views.xml',
        'wizards/wizard_generate_medical_examination.xml',
        'views/hr_employee_views.xml',
        'security/ir.model.access.csv',
        'security/hr_employee_medical_examination_security.xml',
    ],
    "installable": True,
    "license": "AGPL-3",
}