# -*- coding: utf-8 -*-

# Copyright (C) Stefanini Sysman SAS.
# Co-Author        Juan Sebastian Correa(Stefanini Sysman SAS), e_jsacevedo@@sysman.com.co
#                  Juan David Pelaez (Stefanini Sysman SAS), jdsoto1@sysman.com.co
#                  Jhair Alejandro Escobar (Stefanini Sysman SAS), e_japulido@sysman.com.co

{
    "name": "Colombia - Accounting Extended",
    "category": "Localization",
    "version": "15.0.1",
    "author": "Stefanini Sysman SAS",
    "website": "https://sysman.com.co",
    'license': 'OPL-1',
    "summary": "Módulo con ajustes de contabilidad extendidos de la localización Odoo Enterprise - Colombia",
    'description': """
Ajustes de Localización Colombia como base de los proyectos de Stefanini Sysman SAS
========================
Este módulo funciona únicamente con Odoo Enterprise. Hereda l10n_co_edi para permitir que sea este último quien genera la principal
configuración asociada a la facturación electrónica Colombiana.

Este módulo se encarga de realizar los ajustes a los módulos financieros que son requeridos de manera transversal en cualquier proyecto de Stefanini Sysman

Es un módulo que debe ser incluido como dependencia a la hora de realizar cambios en el estándar de financiero y contabilidad dispuesto por odoo.

Cualquier método de los módulos financieros que deba ser sobreescrito pertenece a este módulo.

Ajustes de financiero que únicamente apliquen a ciertas industrias o clientes, deben ir con opciones de activación que le permitan al usuario
decidir si usa esta caracteriztica o no.

Este módulo debe permitir que el cliente pueda usar sin problema la facturación electrónica de Carvajal(l10n_co_edi) o el conector directo con la DIAN, y poder cambiar entre ellos si así es necesario.

Este módulo podría funcionar como un submódulo y permitir que Stefanini Sysman pueda lanzar actualizaciones generales a todos sus clientes.

""",
    "depends": ["base", "account", "l10n_co_edi",],
    "data": [
        "security/ir.model.access.csv",
        "views/account_invoice_discrepancy_response_code_views.xml",
        "views/res_partner_views.xml",
        "views/account_invoice_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/account_payment_views.xml",
    ],
    "installable": True,
}
