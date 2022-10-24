# -*- coding: utf-8 -*-


{
    'name': 'HR Contract Sena',
    'version': '15.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'Stefanini Sysman',
    'company': 'Stefanini Sysman S.A.S',
    'website': 'https://sysman.com.co/',
    'depends': [
        'hr_contract',
        'hr_recruitment',
        'hr_payroll_extended',
        'hr_payroll_variations',
        'board',
    ],
    'data': [
        'views/inherited_hr_contract_view.xml',
        'views/hr_contract_sena.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'AGPL-3',
}
