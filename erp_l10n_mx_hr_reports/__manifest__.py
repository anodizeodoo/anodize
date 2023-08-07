# -*- coding: utf-8 -*-
{
    'name': "ERP MX HR Reports",
    'version': "16.0.0.0",
    'category': "HR PAYROLL",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        ANODIZE HR PAYROLL
    """,
    'depends': ['base', 'hr_payroll', 'report_xlsx'],
    'data': [
        'report/payroll_templates.xml',
        'report/payroll_report_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
}