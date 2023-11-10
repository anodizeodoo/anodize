# -*- coding: utf-8 -*-
{
    'name': "Generate Massive Payment Por Payroll",
    'summary': """
        Allow generate massive payment for payroll""",
    'description': """
        Allow generate massive payment for payroll in txt format
    """,
    "author": "Soltein SA de CV",
    "website": "https://www.soltein.net",
    'version': '16.0.1.0.0',
    "category": "Human Resources/Payroll",
    "license": "AGPL-3",
    'depends': [
        'erp_l10n_mx_hr_payroll_e8e_vauxo',
        ],
    'data': [
        'data/seq_hr_payslips_masive_payment.xml',
        'data/loyout_configuration_bancomer_data.xml',
        'data/loyout_configuration_banorte_data.xml',
        'data/loyout_configuration_santander_data.xml',
        'data/loyout_configuration_bajio_data.xml',
        'security/ir.model.access.csv',
        'wizard/payroll_masive.xml',
        'views/hr_payslip_massive_payment_view.xml',
        'views/res_bank_views.xml',
        
    ],
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
}