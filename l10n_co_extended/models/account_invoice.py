# -*- coding: utf-8 -*-
# Copyright 2019 Juan Camilo Zuluaga Serna <Github@camilozuluaga>
# Copyright 2019 Joan Marín <Github@JoanMarin>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class AccountInvoice(models.Model):
	_inherit = "account.move"


	def _get_zzz(self):
		zz_id = False
		if self.sudo().env['ir.model'].search([('model','=','account.payment.mean.code')]):
			zz_id = self.env['account.payment.mean.code'].search([('code','=','ZZZ')])
		if zz_id:
			return zz_id.id
		return False

	"""
	discrepancy_response_code_id   = fields.Many2one(
		comodel_name='account.invoice.discrepancy.response.code',
		string='Correction concept for Refund Invoice',)
	"""

	refund_type = fields.Selection(
		[('debit', 'Debit Note'),
		 ('credit', 'Credit Note')],
		index=True,
		string='Refund Type',
		track_visibility='always')
	debit_origin_id = fields.Many2one('account.move', 'Factura Debitada', readonly=True, copy=False)
	debit_note_ids = fields.One2many('account.move', 'debit_origin_id', 'Notas Débito', help="Las notas débito creadas a esta factura")
	debit_note_count = fields.Integer('Número de notas débito', compute='_compute_debit_count')

	payment_mean_id = fields.Many2one(
		comodel_name='account.payment.mean',
		string='Payment Method',
		copy=False,
		default=False)

	"""payment_mean_code_id = fields.Many2one('account.payment.mean.code',
		string='Mean of Payment',
		copy=False,
		default=_get_zzz)"""
	invoice_date = fields.Date(default=fields.Date.today()) # datetime.now().date()

	@api.depends('debit_note_ids')
	def _compute_debit_count(self):
		debit_data = self.env['account.move'].read_group([('debit_origin_id', 'in', self.ids)],
		                                                ['debit_origin_id'], ['debit_origin_id'])
		data_map = {datum['debit_origin_id'][0]: datum['debit_origin_id_count'] for datum in debit_data}
		for inv in self:
			inv.debit_note_count = data_map.get(inv.id, 0.0)
	
	def action_view_debit_notes(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Notas Débito'),
			'res_model': 'account.move',
			'view_mode': 'tree,form',
			'domain': [('debit_origin_id', '=', self.id)],
		}
	
	def _get_sequence(self):
		''' Return the sequence to be used during the post of the current move.
		:return: An ir.sequence record or False.
		'''

		res = super(AccountInvoice, self)._get_sequence()
		journal = self.journal_id
		if self.move_type == 'out_invoice' and self.refund_type == 'debit' and journal.debit_note_sequence_id:
			return journal.debit_note_sequence_id
		return res


	def write(self, vals):        
		res = super(AccountInvoice, self).write(vals)

		if vals.get('invoice_date'):
			for invoice in self:
				invoice._onchange_invoice_dates()

		return res

	@api.model
	def create(self, vals):
		res = super(AccountInvoice, self).create(vals)
		res._onchange_recompute_dynamic_lines()
		#res._onchange_invoice_dates()
		return res

	"""
	@api.onchange('invoice_date', 'invoice_date_due', 'invoice_payment_term_id')
	def _onchange_invoice_dates(self):
		payment_mean_obj = self.env['ir.model.data']
		time = 0
		invoice_date = self.invoice_date if self.invoice_date else fields.Date.context_today(self)
		if self.invoice_payment_term_id:
			time = sum([x.days for x in self.invoice_payment_term_id.line_ids])
		
		if (invoice_date == self.invoice_date_due and not self.invoice_payment_term_id) \
			or (self.invoice_payment_term_id and time == 0):
			id_payment_mean = payment_mean_obj._xmlid_lookup(
				'l10n_co_extended.account_payment_mean_2')[1]
			#payment_mean_id = self.env['account.payment.mean'].browse(id_payment_mean)
            payment_mean_id = self.env['l10n_co_edi.payment.option'].browse(id_payment_mean)
		else:
			id_payment_mean = payment_mean_obj._xmlid_lookup(
				'l10n_co_extended.account_payment_mean_2')[1]
			payment_mean_id = self.env['account.payment.mean'].browse(id_payment_mean)

		self.payment_mean_id = payment_mean_id
    """
	
	@api.onchange('partner_id')
	def _onchange_partner_id(self):
		res = super(AccountInvoice, self)._onchange_partner_id()
		#self._onchange_invoice_dates()
		return res