# -*- coding: utf-8 -*-
{
    'name': "smtp_by_user",

    'summary': """
        one server available by user for correct relay while send email""",

    'description': """

    """,

    'author': "Sysman Stefanini",
    'contributors': ['Jhair Escobar e_japulido@sysman.com.co'],
    'website': "http://www.sysman.com.co",
    'category': 'Mailing',
    'version': '15.1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_users_views.xml',
    ],
}
