# -*- coding: utf-8 -*-
# Co-Author        Juan Sebastian Correa(Stefanini Sysman SAS), e_jsacevedo@@sysman.com.co
#                  Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@sysman.com.co

{
    "name": "Facturación Electrónica DIAN",
    "category": "Localization",
    "version": "15.0.1",
    "author": "Stefanini Sysman SAS",
    "website": "http://www.sysman.com.co",
    'license': 'OPL-1',
    "summary": "Facturación Electrónica DIAN",
    "depends": ["l10n_co_extended", "l10n_co", "l10n_latam_base", "web"],
    'external_dependencies': {
        'python': [
            'validators',
            'OpenSSL',
            'xades',
        ],
    },
    "data": [
        'security/ir.model.access.csv',
        "data/account_edit_data.xml",
        "views/account_invoice_views.xml",
        "views/account_invoice_dian_document_views.xml",
        "views/account_journal_views.xml",
        "views/res_company_views.xml",
        "views/product_template_views.xml",
        "views/account_move_approve.xml",
        "data/product_scheme_data.xml",
        "data/cron_acp_tacita_dian.xml",
        "report/account_move_invoice_report.xml",
    ],
    "installable": True,
}
