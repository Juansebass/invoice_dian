# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@sysman.com.co

{
    'name': "Generador de txt para pago de nomina en portal bancario",

    'summary': """
        Permite generar archivo TXT desde la nómina de odoo para subir el pago al portal bancario.""",

    'description': """
        Permite generar archivo TXT desde la nómina de odoo para subir el pago al portal bancario.
    """,

    'author': "Stefanini Sysman SAS",
    'contributors': ['Jhair Escobar e_japulido@sysman.com.co'],
    'website': "http://www.sysman.com.co",
    'category': 'Accounting/Accounting',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_bank_payment_txt_generator', 'hr_payroll'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_bank_txt_config_views.xml',
        'views/hr_payslip_run_views.xml',
        'views/hr_payslip_views.xml',
        # 'views/payment_type_views.xml',
        'wizards/payment_txt_generator_hr_wizard_views.xml',
    ],
}
