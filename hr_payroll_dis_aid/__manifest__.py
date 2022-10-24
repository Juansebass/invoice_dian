# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Payroll Discounts',
    'summary': 'HR Payroll Employee Discount like liens, loans, etc or Aid for Sysman',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'website': "https://sysman.com.co",
    'author': 'Stefanini Sysman',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': ['hr_contract_completion'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/refinancing_wizard.xml',
        'wizard/debt_capacity_wizard.xml',
        'wizard/confirm_cancel_wizard.xml',
        'wizard/confirm_finish_wizard.xml',
        'data/hr_payroll_debt_capacity_data.xml',
        'views/hr_dis_aid_views.xml',
        'views/res_partner_views.xml',
        'views/inherit_hr_employee_views.xml',
        'views/hr_payroll_debt_capacity_views.xml',
        'views/inherited_hr_payslip_view.xml',
        'views/hr_court_views.xml',
        'views/hr_pv_views.xml',

    ],
}
