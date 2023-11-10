# -*- coding: utf-8 -*-
{
    'name': "HR Employee Relatives Scholarship",
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'website': "https://www.soltein.net",
    'author': "Viixoo & Soltain",
    'summary': """Allows storing information about employee family and grade""",
    'depends': [
        'erp_hr_relatives',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_scholarship_grade_views.xml',
        'views/hr_employee_relative_views.xml',
        'views/res_config_settings_views.xml',
        'views/hr_menus.xml',
    ],
}
