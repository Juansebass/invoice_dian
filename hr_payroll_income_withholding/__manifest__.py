
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# -*- coding: utf-8 -*-

{
    'name': 'Payroll Income Withholding',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'website': 'hhttps://sysman.com.co',
    'category': 'Human Resources',
    'summary': "Module to manage income withholding in payroll of employee",
    'depends': ['hr_contract_completion'],
    'data': [
        'data/ir_cron_data.xml',
        'views/hr_payroll_income_withholding_view.xml',
        'views/hr_pv_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False
}
