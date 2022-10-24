# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_generate_txt_wizard(self):
        ctx = self._context.copy()
        if not ctx.get('default_company_id', False):
            ctx.update({'default_company_id': self.env.company.id,})
        if len(self) > 1:
            ctx.update({'active_model': self._context.get('active_model'),
                        'active_ids': self._context.get('active_ids')})
        return {
            'name': _('Generar Txt'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'payment.txt.generator.hr.wizard',
            'context': ctx,
            # 'view_id': False,
            'target':'new'
        }