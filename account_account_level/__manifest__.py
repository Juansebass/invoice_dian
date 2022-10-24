# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@sysman.com.co

{
    'name': "Reporte por Niveles de Cuenta",

    'summary': """
        Niveles Fijos de cuenta y esquema de cuenta padre en plan contable""",

    'description': """
        Niveles Fijos de cuenta y esquema de cuenta padre en plan contable usados para filtrar el
        reporte de balance de prueba y poder obtener un balance inicial y final por terceros y por niveles.
    """,

    'author': "Stefanini Sysman",
    'website': "http://www.sysman.com.co",
    'category': 'Accounting',
    'version': '15.0.1',

    'depends': [
        'base',
        'account',
        'account_accountant'
    ],

    'data': [
        'views/account_account_level.xml',
        'report/xls_partner_balance_report.xml',
    ]
}
