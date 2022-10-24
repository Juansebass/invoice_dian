
{
    'name': 'Hr Payroll Extra Hours',
    'version': '15.0.1.0.0',
    'summary': 'Module to load and store SIR File Group.',
    'category': 'Human Resources',
    'author': 'Darshan Patel',
    'license': 'AGPL-3',
    'maintainer': 'Darshan Patel',
    'company': 'Pyc Solution',
    'website': 'https://pycsolution.co',
    'depends': [
        'hr_payroll'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_extra_hours_data.xml',
        'views/hr_ehours_sir_view.xml',
        'views/hr_ehours_pres_subs_view.xml',
        'views/hr_extra_hours_conf_view.xml',
        'views/cargue_horas_extras_view.xml',
        'views/overtime_settlement_view.xml',
    ],
    'installable': True,
    'application': True,
}
