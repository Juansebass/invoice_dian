# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = 'account.payment'


    purchase_order_id = fields.Many2one(
        'purchase.order', string='Purchase Order', required=False, index=True, 
        states={'draft': [('readonly', False)]}, readonly=True)
    payment_date = fields.Date(related="move_id.date", store=True)


    @api.onchange('partner_id')
    def _onchange_partner_purchase(self):
        if self.partner_id:
            self.purchase_order_id = False


    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        self.purchase_import_id = False
        if self.purchase_order_id and self.purchase_order_id.purchase_import_id:
            self.purchase_import_id = self.purchase_order_id.purchase_import_id


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
