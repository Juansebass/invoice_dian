# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountMoveReversal(models.TransientModel):

    _inherit = "account.move.reversal"

    def _prepare_default_reversal(self, move):
        """ Set the document refund_type as credit note """
        res = super()._prepare_default_reversal(move)
        if move.move_type and move.move_type in ('out_invoice','out_refund'):
            res.update({
                'refund_type': 'credit',
                'l10n_co_edi_description_code_credit': self.l10n_co_edi_description_code_credit or False,
                'l10n_co_edi_payment_option_id': move.l10n_co_edi_payment_option_id.id or False,
            })
        elif move.move_type and move.move_type == 'in_invoice':
            res.update({
                'refund_type': 'debit',
            })
        return res