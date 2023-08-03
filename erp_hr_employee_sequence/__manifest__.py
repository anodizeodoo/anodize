# -*- coding: utf-8 -*-

{
    'name': "ERP Employee Sequence",
    'version': "16.0.1.1",
    'category': "HR",
    'author': 'Soltein SA de CV',
    'website': 'http://www.soltein.net',
    "license": "AGPL-3",
    "description": """
        ERP Employee Sequence
    """,
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_employee_sequence.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'views/ir_sequence_views.xml'
    ],
    'installable': True,
}