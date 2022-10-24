# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.tools.float_utils import float_compare
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT, float_repr, float_round
from odoo.tools import html2plaintext
from odoo.exceptions import ValidationError
from requests import post, exceptions
#from .carvajal_request import CarvajalRequest

import pytz
import base64
import re

from collections import defaultdict
from datetime import timedelta
from functools import lru_cache


class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    # -------------------------------------------------------------------------
    # BUSINESS FLOW: EDI
    # -------------------------------------------------------------------------

    def _check_move_configuration(self, move):
        # OVERRIDE
        """
        Este método se sobrescribe para garantizar el correcto diligenciamiento del formulario
        con la información requerida para la conexión directa con la DIAN.
        Contrario al método original, que valida la información de configuración de carvajal.

        TODO: Los módulos deben poderse ejecutar al tiempo, podrían darse caso de una empresa reportando directo a la DIAN
        y la otra reportando a Carvajal.
        """
        self.ensure_one()

        company = move.company_id
        journal = move.journal_id
        now = fields.Datetime.now()
        oldest_date = now - timedelta(days=5)
        newest_date = now + timedelta(days=10)

        #edi_result = super()._check_move_configuration(move)
        edi_result = []
        if (
            not company.l10n_co_edi_username 
            or not company.l10n_co_edi_password 
            or not company.l10n_co_edi_company 
            or not company.l10n_co_edi_account
        ) and (not company.einvoicing_enabled):
            edi_result.append(_("DIAN credentials are not set on the company, please go to Accounting Settings and set the credentials."))

        if (
            move.move_type != 'out_refund' 
            and not move.debit_origin_id
        ) and (
            not journal.l10n_co_edi_dian_authorization_number 
            or not journal.l10n_co_edi_dian_authorization_date 
            or not journal.l10n_co_edi_dian_authorization_end_date
        ):
            edi_result.append(_("'Resolución DIAN' fields must be set on the journal %s", journal.display_name))

        if not move.partner_id._get_vat_without_verification_code():
            edi_result.append(_("You can not validate an invoice that has a partner without VAT number."))

        if not move.company_id.partner_id.l10n_co_edi_obligation_type_ids:
            edi_result.append(_("'Obligaciones y Responsabilidades' on the Customer Fiscal Data section needs to be set for the partner %s.", move.company_id.partner_id.display_name))

        if not move.partner_id.commercial_partner_id.l10n_co_edi_obligation_type_ids:
            edi_result.append(_("'Obligaciones y Responsabilidades' on the Customer Fiscal Data section needs to be set for the partner %s.", move.partner_id.commercial_partner_id.display_name))

        if (move.l10n_co_edi_type == '2' and \
            any(l.product_id and not l.product_id.l10n_co_edi_customs_code for l in move.invoice_line_ids)):
            edi_result.append(_("Every exportation product must have a customs code."))
        elif move.invoice_date and not (oldest_date <= fields.Datetime.to_datetime(move.invoice_date) <= newest_date):
            move.message_post(body=_('The issue date can not be older than 5 days or more than 5 days in the future'))
        elif any(l.product_id and not l.product_id.default_code and \
                 not l.product_id.barcode and not l.product_id.unspsc_code_id for l in move.invoice_line_ids):
            edi_result.append(_("Every product on a line should at least have a product code (barcode, internal, UNSPSC) set."))

        if not move.company_id.partner_id.l10n_latam_identification_type_id:
            edi_result.append(_("The Identification Number Type on the customer\'s partner should be set."))

        if not move.partner_id.commercial_partner_id.l10n_latam_identification_type_id:
            edi_result.append(_("The Identification Number Type on the customer\'s partner should be set."))

        if self.code != 'ubl_dian_connector':
            return edi_result

        return edi_result

    def _l10n_co_post_invoice_step_1(self, invoice):
        '''
        Sends the xml to carvajal. Override to send directly to the DIAN
        TODO: Los módulos deben poderse ejecutar al tiempo, podría darse el caso de una empresa reportando directo a la DIAN
        y la otra reportando a Carvajal.
        '''
        response = []
        try:
            response = invoice._post_dian()
        except exceptions.RequestException as e:
            raise ValidationError("Unknown Error: %s\n\nContact with your administrator." % (e))

        return response


    def _post_invoice_edi(self, invoices):
        # OVERRIDE
        self.ensure_one()
        if self.code != 'ubl_dian_connector':
            return super()._post_invoice_edi(invoices)

        invoice = invoices  # No batching ensures that only one invoice is given as parameter
        if not invoice.l10n_co_edi_transaction:
            return {invoice: self._l10n_co_post_invoice_step_1(invoice)}
        else:
            return {invoice: self._l10n_co_post_invoice_step_2(invoice)}

    def _cancel_invoice_edi(self, invoices):
        # OVERRIDE
        self.ensure_one()
        return {invoice: {'success': True} for invoice in invoices}  # By default, cancel succeeds doing nothing.
