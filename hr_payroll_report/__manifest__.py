# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Payroll Report',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'summary': 'Hr Payroll Report Customization for Sysman',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'company': 'Stefanini Sysman SAS',
    'website': "https://sysman.com.co",
    'depends': [
        'hr_payroll_extended',
        'hr_contract_extended',
        'base_address_city',
        'hr_employee_extended',
        'hr_reports_config',
        'account_reports'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/inherited_res_partner_view.xml',
        'views/inherited_hr_employee_view.xml',
		'wizard/zconcept_wizard_view.xml',
		'wizard/zprenomina_wizard_view.xml',
        # 'views/hr_risk_type_view.xml',
        'views/inherited_hr_contract_view.xml',
        # 'views/hr_contributor_type_view.xml',
        'views/inherited_res_city_view.xml',
        'views/inherited_res_company_view.xml',
        'views/hr_payroll_pila_view.xml',
        'reports/menu_items_reports.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
