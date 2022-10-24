# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    is_einvoicing = fields.Boolean(string='Electronic invoicing?')    
    resolution_text = fields.Text(string='Resolution')
    technical_key = fields.Text(string='Technical Key')
    terms = fields.Text(string='Terminos y condiciones')
    payment_info = fields.Text(string='Instrucciones de pago')
    