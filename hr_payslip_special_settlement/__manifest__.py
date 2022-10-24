# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Payslip Settlement',
    'version': '15.0.1.0.0',
    'summary': """ """,
    'sequence': 15,
    'category': 'Human Resources',
    'author': 'Stefanini Sysman',
    'license': 'AGPL-3',
    'maintainer': 'Stefanini Sysman',
    'company': 'Stefanini Sysman S.A.S',
    'website': 'https://sysman.com.co/',
    'description': """
    """,
    'depends': ['hr_payroll', 'hr_payroll_variations'],
    'data': [
        'security/ir.model.access.csv',
        'views/type_settlement_view.xml',
        'views/assign_month_view.xml',
        'views/inherited_hr_payslip_view.xml'
    ],
    'installable': True,
    'application': True,
}
