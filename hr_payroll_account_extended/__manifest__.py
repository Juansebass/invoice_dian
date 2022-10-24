# -*- coding: utf-8 -*-

{
    'name': 'HR Payroll Account Extended',
    'summary': 'HR Payroll Account Customization for Sysman',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'website': 'https://sysman.com.co',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'hr_payroll_account',
    ],
    'data': [
        'view/hr_salary_rule_view.xml',
    ],
}
