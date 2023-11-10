# -*- coding: utf-8 -*-
{
    "name": "Experience Management",
    "version": "16.0.1.0.0",
    "author": "Soltein SA de CV",
    "website": "https://www.soltein.net",
    'category': 'Human Resources/Employees',
    "depends": ["hr"],
    "data": [
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/hr_academic_view.xml",
        "views/hr_professional_view.xml",
        "views/hr_certification_view.xml",
        "report/employee_resume_report_pdf.xml",
    ],
    'installable': True,
    "license": "AGPL-3",
}