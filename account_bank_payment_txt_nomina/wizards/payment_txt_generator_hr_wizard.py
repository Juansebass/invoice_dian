# -*- coding: utf-8 -*-
from base64 import b64encode, b64decode
from datetime import datetime
from pytz import timezone

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PaymentTxtGeneratorHrWizard(models.TransientModel):
    _name = 'payment.txt.generator.hr.wizard'
    _description = 'Txt generator hr'

    def _get_txt_setting_ids(self):
        txt_setting_ids = []

        if self.bank_id:
            txt_setting_obg = self.env['res.bank.txt_config']
            txt_setting_ids = txt_setting_obg.search([('bank_id','=', self.bank_id.id), ('state','=','active')]).ids

        return [('id', 'in', txt_setting_ids)]

    name = fields.Char(string='Nombre')
    transmission_date = fields.Datetime(string="Fecha de transmisión", default=fields.Datetime.now)
    date = fields.Date(string='Fecha Pago', default=fields.Date.today)
    
    journal_id = fields.Many2one('account.journal', string='Banco')
    
    txt_setting_id = fields.Many2one('res.bank.txt_config', 'Plantilla Banco') #, domain=_get_txt_setting_ids)
    company_id = fields.Many2one('res.company', string='Compañia')
    txt_filename = fields.Char(string="Nombre de archivo txt")
    txt_file = fields.Binary(string="Archivo Txt")
    payment_type_id = fields.Many2one('payment.type', string="Tipo de pago")

    @api.onchange('journal_id')
    def _onchange_bank_id(self):
        bank_ids = []
        if self.journal_id:
            bank_ids.append(self.journal_id.bank_id.id)
        return {
            'domain': {'txt_setting_id': [('bank_id','in',bank_ids)],
                       'payment_type_id': [('bank_id','in',bank_ids)]}
        }
    
    def generate_txt_nomina(self):
        self.ensure_one()
        header_id = self
        detail_ids = False
        txt_setting_obg = self.env['res.bank.txt_config']
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        active_model_obj = self.env[active_model]
        active_model_ids = active_model_obj.browse(active_ids)

        if active_model == 'hr.payslip':
            detail_ids = active_model_ids
        elif active_model == 'hr.payslip.run':
            detail_ids = active_model_ids.slip_ids

        bank_id = self.journal_id.bank_id or False
        if not bank_id:
            raise ValidationError(_('Bank not found'))

        if self.txt_setting_id:
            txt_setting_id = self.txt_setting_id
        else:
            txt_setting_id = txt_setting_obg.search([('bank_id','=',bank_id.id),('state','=','active')], limit=1)

        if not txt_setting_id:
            raise ValidationError(_('No txt configuration record found for bank %s') % bank_id.name)
        
        var_ava = self.get_var_ava_nomina(header_id, detail_ids)
        txt = txt_setting_id.get_txt_nomina(header_id, detail_ids, var_ava)
        
        txt_filename = 'PAGO_' + \
                                header_id.name + \
                                '_' + \
                                bank_id.name + \
                                '_' + \
                                var_ava['date_transmission'].strftime('%d-%m-%Y %H:%M:%S') + \
                                '.txt'
        txt_file = b64encode(txt.encode('utf-8')).decode('utf-8', 'ignore')
        
        if active_model == 'hr.payslip.run':
            active_model_ids.write({'txt_file': txt_file, 'txt_filename': txt_filename,})
        else:
            self.write({'txt_file': txt_file, 'txt_filename': txt_filename,})
            attachment = self.env['ir.attachment'].create({
                        'name': txt_filename,
                        # 'datas_fname': txt_filename,
                        'datas': txt_file,
                    })
            return {
                        'type': 'ir.actions.act_url',
                        'url': self.env['ir.config_parameter'].get_param('web.base.url') + '/web/content/%s?download=true' % (attachment.id),
                        # 'target': 'new',
                        'nodestroy': False,
                    }

    def get_var_ava_nomina(self, header, detail):
        return {
            'company_name': header.company_id.name,
            'company_street': header.company_id.partner_id.street,
            'date_payment': header.date,
            'date_transmission': header.transmission_date.astimezone(timezone(self.env.user.tz)),
            'amount_total': sum([x.total_amount for x in detail]),
            'number_lines': len(detail),
            'dispersing_account': header.journal_id.bank_acc_number,

            'beneficiary_name': '',
            'beneficiary_street': '',
            'amount_line': '',
            'circular': '',
            'item': '',
        }    
