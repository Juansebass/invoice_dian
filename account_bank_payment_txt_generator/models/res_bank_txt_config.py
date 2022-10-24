# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging

_logger = logging.getLogger(__name__)



class ResBankTxtConfig(models.Model):
    _name = 'res.bank.txt_config'
    _description = 'Configuration of txt generator of each banks for payments in the banking portal'
    _rec_name = 'bank_id'


    name = fields.Char('Description')
    bank_id = fields.Many2one('res.bank', string='Bank')
    header_line_id = fields.One2many('res.bank.txt_config.line', 'header_setting_id', string='Txt Header')
    body_line_id = fields.One2many('res.bank.txt_config.line', 'body_setting_id', string='Txt Body')
    footer_line_id = fields.One2many('res.bank.txt_config.line', 'footer_setting_id', string='Txt Footer')
    state = fields.Selection([('active', 'Active'),
                              ('incative', 'Inactive'),], string='State', default="active")


    @api.depends('bank_id', 'name')
    def name_get(self):
        result = []
        for txt_config in self:
            name = txt_config.bank_id.name + ' (' + str(txt_config.name or txt_config.id) + ')'
            result.append((txt_config.id, name))
        return result


    def get_txt(self, batch_payment, var_ava):
        self.ensure_one()
        txt = ''
        if not batch_payment:
            raise ValueError(_('There is no payment batch document to process'))
        if not batch_payment.payment_ids:
            raise ValueError(_('There is no payment document to process'))

        if self.header_line_id:
            txt += self.get_txt_line('header', batch_payment, False, var_ava)
        if self.body_line_id:
            item = 0
            for line in batch_payment.payment_ids:
                item += 1
                var_ava = dict(var_ava, **{
                    'beneficiary_name': line.partner_id.name or '',
                    'beneficiary_street': line.partner_id.street or '',
                    'beneficiary_vat': line.partner_id.vat or '',
                    'beneficiary_bank_id': line.partner_bank_id.acc_number or '',
                    'beneficiary_bic': line.partner_bank_id.bank_id.bic or '',
                    'beneficiary_bank_zip': line.partner_bank_id.bank_id.zip or '',
                    'beneficiary_bank_type': '32' if line.partner_bank_id.account_type == 'ahorros' else '22',
                    'amount_line': str(round((line.amount*10), 2)).replace('.','') or '',
                    'circular': line.ref or '',
                    'item': item,
                })
                txt += self.get_txt_line('body', batch_payment, line, var_ava)
        if self.footer_line_id:
            txt += self.get_txt_line('footer', batch_payment, False, var_ava)

        return txt
    
    def get_txt_line(self, type_content, batch_payment, payment, var_ava):
        self.ensure_one()
        txt = ''
        line_fields = self.header_line_id if type_content == 'header' else \
                      self.body_line_id if type_content == 'body' else \
                      self.footer_line_id if type_content == 'footer' else False
        for field in line_fields.sorted(lambda s: s.sequence):
            size = field.size
            size_adjust = field.size_adjust
            align = field.alignment
            fill = field.fill[0]
            val_type = field.value_type
            value = field.value
            txt_field = ''
            
            # calc val field
            if val_type == 'burned':
                txt_field += value
            elif val_type == 'python': 
                txt_field = str(eval(value))
            elif val_type == 'call':
                if 'date_transmission' in value or 'date_payment' in value:
                    #date, formatt = value.split(',')
                    #txt_field = var_ava[date].strftime(formatt)
                    txt_field = str(var_ava[value].strftime('%d%m%y'))
                elif value in var_ava:
                    txt_field = str(var_ava[value])
                else:
                    raise ValidationError(_('The value %s does not belong to one of the available variables') % value)
            # fill
            if len(txt_field) < size:
                dif = size - len(txt_field)
                if align == 'left':
                    txt_field = txt_field + fill*dif
                else:
                    txt_field = fill*dif + txt_field
            elif len(txt_field) > size and size_adjust:
                txt_field = txt_field[0:size]
            elif len(txt_field) > size and not size_adjust:
                raise ValidationError(_('The value exceeds the character size allowed'
                                        'in the %s line of the %s in the banks configuration\n'
                                        'Illegal value: %s') % (field.sequence, type_content, txt_field))
            txt += txt_field
        txt += '\n'
        return txt

    
    
    
