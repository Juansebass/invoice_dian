# -*- coding: utf-8 -*-
from odoo import fields,models


class ResPartnerBank(models.Model):
   _inherit = 'res.partner.bank'

   acc_number = fields.Char(string="Datos Cuenta Bancaria",tracking=True, required="True")
   account_type = fields.Selection([('ahorros', 'AHORROS'),('corriente', 'CORRIENTE')],'Tipo de Cuenta',tracking=True)