# -*- coding: utf-8 -*-
{
    'name': "erp_l10n_mx_hr_payroll_massive_payment",

    'summary': """
        Allow generate massive payment for payroll""",

    'description': """
        Allow generate massive payment for payroll in txt format
    """,

    "author": "Soltein SA de CV",
    "website": "https://www.soltein.net",
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'hr',   
        'hr_payroll',
        'hr_work_entry_contract',
        'erp_l10n_mx_hr_base',
        "erp_l10n_mx_payslip_data",
        "l10n_mx_edi_extended",
        'erp_l10n_mx_hr_payroll_e8e_vauxo',
        ],

    # always loaded
    'data': [
        'data/seq_hr_payslips_masive_payment.xml',
        'security/ir.model.access.csv',
        'wizard/payroll_masive.xml',
        'views/hr_payslip_massive_payment_view.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    "installable": True,
}
