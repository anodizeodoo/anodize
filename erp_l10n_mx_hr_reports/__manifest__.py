# -*- coding: utf-8 -*-
{
    'name': "Mexican HR Reports",
    'version': "16.0.0.0",
    'category': "HR PAYROLL",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        HR Payroll Reports
    """,
    'depends': ['erp_l10n_mx_hr_base', 'report_xlsx'],
    'data': [
        'report/payroll_templates.xml',
        'report/payroll_report_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
}