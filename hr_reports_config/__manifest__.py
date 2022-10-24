# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Hr Reports Config',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'summary': 'Hr Reports Config for Sysman',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'company': 'Stefanini Sysman SAS',
    'website': "https://sysman.com.co",
    'depends': [
        'hr_payroll', 'hr_payroll_variations'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_report_config_data.xml',
        'data/hr_report_config_data_2.xml',
        'data/hr_report_config_data_3.xml',
        'data/hr_pila_report_config_data.xml',
        'views/hr_reports_config_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
