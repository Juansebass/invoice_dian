# -*- coding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Payroll Employee Extended',
    'summary': 'HR Payroll Employee Extended, manage Laboral Certification for Sysman',
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
    'depends': [
        'base',
        'hr_payroll',
        'hr_payroll_variations',
        'hr_management_human_talent',
    ],
    'data': [
        'security/ir.model.access.csv',
        'report/hr_contract_report.xml',
        'report/report_laboral_certification.xml',
        'views/inherited_hr_employee_view.xml',
        'views/inherited_res_company_view.xml',
        'wizard/hr_employee_generate_send_wizard_view.xml',
    ],
}
