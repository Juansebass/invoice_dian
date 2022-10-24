# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from datetime import datetime
from pytz import timezone

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'


    def _get_payment_type(self):
        if self.journal_id and self.journal_id.bank_id:
            payment_type_ids = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False), ('bank_id', '=', self.journal_id.bank_id.id)]).ids
        else:
            payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids
        return [('id', 'in', payment_type_ids)]


    @api.depends('journal_id')
    def _get_employee_depends(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.bank_id:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False), ('bank_id', '=', rec.journal_id.bank_id.id)]).ids
            else:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids

            return {'domain': {'payment_type': [('id', 'in', payment_type_ids)]}}


    @api.onchange('journal_id')
    def _get_employee_onchange(self):
        for rec in self:
            if rec.journal_id and rec.journal_id.bank_id:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), '|', ('bank_id', '=', False), ('bank_id', '=', rec.journal_id.bank_id.id)]).ids
            else:
                payment_type_ids = self.env['payment.type'].search([('active', '=', True), ('bank_id', '=', False)]).ids

            return {'domain': {'payment_type': [('id', 'in', payment_type_ids)]}}


    payment_type = fields.Many2one('payment.type', string="Payment type", domain=_get_payment_type)
    txt_filename = fields.Char(string="Name txt file")
    txt_file = fields.Binary(string="Txt file")


    def generate_txt(self):
        txt_setting_obg = self.env['res.bank.txt_config']
        for record in self:
            bank_id = record.journal_id.bank_id or False
            if not bank_id:
                raise ValidationError(_('Bank not found'))
            txt_setting_id = txt_setting_obg.search([('bank_id','=',bank_id.id),('state','=','active')], limit=1)
            if not txt_setting_id:
                raise ValidationError(_('No txt configuration record found for bank %s') % bank_id.name)
            txt = txt_setting_id.get_txt(record)
            date_txt = datetime.now(timezone(self.env.user.tz or 'GTM'))
            record.txt_filename = 'PAGO_'+ record.name + '_' + bank_id.name + '_' + date_txt.strftime('%d-%m-%Y %H:%M:%S') +'.txt'
            record.txt_file = b64encode(txt.encode('utf-8')).decode('utf-8', 'ignore')

    # def get_variables_availables(self):

    #     return {
    #         'company_name': self.journal_id.company_id.name,
    #         'company_nit': ,
    #         'company_nit_dv': ,
    #         'date_payment': ,

    #     }    
    
