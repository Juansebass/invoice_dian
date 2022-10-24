# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Pv Conciliate',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'summary': 'Hr Pv Conciliate',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'company': 'Stefanini Sysman',
    'website': 'https://sysman.com.co/',
    'depends': [
        'hr_payroll_variations',
    ],
    'data': [
        'security/hr_pv_conciliate_security.xml',
        'security/ir.model.access.csv',
        'data/hr_pv_conciliate_data.xml',
        'views/hr_event_range_view.xml',
        'wizard/pv_conciliation_create.xml',
        'wizard/pv_conciliation_line_create.xml',
        'wizard/wizard_pv_conciliation_payslip_view.xml',
        'views/hr_pv_conciliation_view.xml',
        'views/inherited_hr_pv_view.xml',
    ],
    'installable': True,
    'application': False,
}
