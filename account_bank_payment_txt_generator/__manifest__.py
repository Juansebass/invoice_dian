# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@sysman.com.co

{
    'name': "Txt generator for payment in banking portal",

    'summary': """
        It allows to generate TXT file to upload the payment to the banking portal""",

    'description': """
        It allows to generate TXT file to upload the payment to the banking portal
    """,

    'author': "Stefanini Sysman SAS",
    'contributors': ['Jhair Escobar e_japulido@sysman.com.co'],
    'website': "http://www.sysman.com.co",
    'category': 'Accounting/Accounting',
    'version': '15.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account_batch_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/res_bank_txt_config_views.xml',
        'wizards/payment_txt_generator_wizard_views.xml',
        'views/account_batch_payment_views.xml',
        'views/payment_type_views.xml',
    ],
}
