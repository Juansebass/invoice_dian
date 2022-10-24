# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@latam.stefanini.com

{
    'name' : 'Advances on Purchase Order V15 Enterprise',
    'version' : '15.0.1',
    'sequence': 201,
    'category': 'Purchase',
    'author': "S SAS",
    'contributors': ['Jhair Escobar e_japulido@latam.stefanini.com'],
    'website': "http://www.todoo.co",
    'license': '',
    'summary' : 'Module with adjustments to include Advances in the Purchases Order',
    'description' : """
        Module with adjustments to include Advances in the Purchases Order
        ==================================
    """,
    'depends': [
        'purchase',
    ],
    'data' : [
         'views/account_payment.xml',
    ],
    'images': [
        "static/description/logo.png"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
