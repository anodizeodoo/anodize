# -*- coding: utf-8 -*-
{
    "name": "MX Formato Unico de Movimiento de Personal",
    "author": "Soltein SA de CV",
    "website": "https://www.soltein.net",
    "version": "16.0.1.0",
    "category": "Human Resources",
    "depends": [
        'base_address_extended',
        'hr_contract',
        'hr_holidays',
    ],
    "data": [
        'data/data.xml',
        'report/hr_fump_mov_view.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_fump_config_view.xml',
        'views/hr_fump_view.xml',
        'views/hr_contract.xml',
        'views/hr_employee.xml',
        'views/hr_fump_loader_views.xml',
        'views/hr_fump_menu_view.xml',
        'wizard/hr_fump_movement_type_wzd_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': False,
}
