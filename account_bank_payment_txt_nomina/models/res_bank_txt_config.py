# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ResBankTxtConfig(models.Model):
    _inherit = 'res.bank.txt_config'

    is_nomina = fields.Boolean(string='Nómina?', default=False)    

    def get_txt_nomina(self, batch_payment, detail, var_ava):
        self.ensure_one()
        txt = ''
        if not batch_payment:
            raise ValueError(_('There is no payment batch document to process'))
        if not detail:
            raise ValueError(_('There is no payment document to process'))

        if self.header_line_id:
            txt += self.get_txt_line_nomina('header', batch_payment, False, var_ava, detail)
        if self.body_line_id:
            item = 0
            for line in detail:
                item += 1
                var_ava = dict(var_ava, **{
                    'beneficiary_name': line.employee_id.name or '',
                    'beneficiary_street': line.employee_id.complete_direction or '',
                    'amount_line': line.total_amount or '',
                    'circular': line.number or '',
                    'item': item,
                })
                txt += self.get_txt_line_nomina('body', batch_payment, line, var_ava, detail)
        if self.footer_line_id:
            txt += self.get_txt_line_nomina('footer', batch_payment, False, var_ava, detail)

        return txt
    
    def get_txt_line_nomina(self, type_content, batch_payment, payment, var_ava, set_payments):
        self.ensure_one()
        txt = ''
        line_fields = self.header_line_id if type_content == 'header' else \
                      self.body_line_id if type_content == 'body' else \
                      self.footer_line_id if type_content == 'footer' else False
        for field in line_fields.sorted(lambda s: s.sequence):
            size = field.size
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
                    date, formatt = value.split(',')
                    txt_field = var_ava[date].strftime(formatt)
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
            elif len(txt_field) > size:
                raise ValidationError(_('The value exceeds the character size allowed'
                                        'in the %s line of the %s in the banks configuration\n'
                                        'Illegal value: %s') % (field.sequence, type_content, txt_field))
            txt += txt_field
        txt += '\n'
        return txt

    
    
    
