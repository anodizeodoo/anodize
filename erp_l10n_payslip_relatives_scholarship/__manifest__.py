# -*- coding: utf-8 -*-
{
    'name': "Relatives Scholarship payslip",
    'version': '16.0.1.0.0',
    'category': 'Human Resources/Employees',
    'website': "https://www.soltein.net",
    'author': "Viixoo & Soltain",
    'summary': """Compute payslip using Scholarship information""",
    'depends': [
        'erp_hr_relatives_scholarship',
        'erp_l10n_mx_hr_base',
        'report_xlsx',
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_salary_rule_views.xml',
        'views/hr_sholarship_registration_views.xml',
        'views/hr_scholarship_grade_views.xml',
        'reports/hr_scholarship_registration_report.xml',
        'wizards/hr_scholarship_registration_wizard.xml',
        'views/menus.xml',
    ],
}
