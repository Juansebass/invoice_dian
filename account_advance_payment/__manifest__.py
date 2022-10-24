# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@latam.stefanini.com

{
    'name' : 'Account Advance Payment',
    'version' : '15.0.1',
    'sequence': 201,
    'category': 'Purchase',
    'author': "Stefanini Sysman SAS",
    'contributors': ['Jhair Escobar e_japulido@latam.stefanini.com'],
    'website': "http://www.sysman.com.co",
    'license': '',
    'summary' : 'Account Advance Payment',
    'description' : """
        Account Advance Payment
        ==================================
    """,
    'depends': [
        'account',
        'hr_expense',
        'purchase',
    ],
    'data' : [
         'security/security_group.xml',
         'security/ir.model.access.csv',
         'data/ir.sequence.xml',
         'views/account_advance_payment.xml',
         'wizard/account_advance_register_payment.xml'
    ],
    'images': [
        "static/description/logo.png"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
