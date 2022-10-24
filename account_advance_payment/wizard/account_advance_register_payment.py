# -*- coding: utf-8 -*-
from lxml import etree

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from datetime import datetime
from collections import defaultdict
import json


import logging

_logger = logging.getLogger(__name__)


class AccountAdvancePaymentRegister(models.TransientModel):
    _name = 'account.advance.payment.register'
    _description = 'Registrar Pago de Anticipos'

    # == Business fields ==
    payment_date = fields.Date(string="Fecha del Pago", required=True,
        default=fields.Date.context_today, track_visibility="onchange")
    amount = fields.Monetary(currency_field='currency_id', store=True, readonly=True,
        compute='_compute_amount', string='Valor a Pagar', track_visibility="onchange")
    communication = fields.Char(string="Memo", store=True, readonly=False,
        compute='_compute_communication')
    currency_id = fields.Many2one('res.currency', string='Currency', store=True, readonly=False,
        compute='_compute_currency_id',
        help="The payment's currency.")
    journal_id = fields.Many2one('account.journal', string='Diario',
        domain="[('type', 'in', ('bank', 'cash'))]")
    available_partner_bank_ids = fields.Many2many(
        comodel_name='res.partner.bank')
    partner_type = fields.Selection([
        ('supplier', 'Proveedor'),
    ], copy=False, string='Tipo de Tercero', default='supplier')
    payment_type = fields.Selection([
        ('outbound', 'Envíar Dinero'),
        #('inbound', 'Receive Money'),
    ], string='Tipo de Pago', copy=False, default='outbound') #TODO: agregar soporte para anticipos recibidos
    partner_bank_id = fields.Many2one(
        comodel_name='res.partner.bank',
        string="Cuenta Bancaría",
        readonly=False,
        store=True,
        domain="[('id', 'in', available_partner_bank_ids)]",
    )
    payment_method_line_id = fields.Many2one('account.payment.method.line', string='Payment Method',
        readonly=False, store=True, copy=False,
        compute='_compute_payment_method_line_id',
        domain="[('id', 'in', available_payment_method_line_ids)]")
    partner_id = fields.Many2one('res.partner',
        string="Proveedor", store=True, copy=False, ondelete='restrict',
        compute='_compute_from_lines', track_visibility="onchange")
    advance_ids = fields.One2many('account.advance.payment.register.line', 'wizard_id', 'Anticipos', readonly=False, required=True)
    payment_has_exchange_rate = fields.Boolean('Aplicar TRM por documento')
    payment_exchange_rate = fields.Float('TRM de este pago', default=1, track_visibility="onchange")
    payment_exchange_allow_ok = fields.Boolean('Permitir TRM por documento', compute="_compute_payment_exchange_allow")
    currency_rate = fields.Float(
        "TRM Nativa",
        compute='_compute_currency_rate', 
        compute_sudo=True,
        store=True,
        digits=(12, 6),
        readonly=True,
        track_visibility="onchange",
        help='TRM aplicada por Odoo nativamente, definida en la moneda de la empresa'
    )
    company_currency_id = fields.Many2one(related='journal_id.company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    company_id = fields.Many2one('res.company', store=True, copy=False, default=lambda self: self.env.company)
    amount_signed = fields.Monetary(
        string='Moneda Local',
        store=True,
        readonly=True,
        #compute='_compute_amount_signed',
        currency_field='company_currency_id'
    )
    payment_group = fields.Boolean('Pago Agrupado')


    @api.depends('journal_id', 'payment_date', 'company_id','currency_id')
    def _compute_currency_rate(self):
        for payment in self:
            date = self._context.get('date') or datetime.today()
            company_currency = payment.journal_id.company_id.currency_id or self.env.company.currency_id
            journal_currency = payment.journal_id.currency_id or company_currency
            payment_currency = payment.currency_id or company_currency
            currency = payment.currency_id.id
            if payment_currency == journal_currency:
                currency = payment_currency.id
            self.env['res.currency.rate'].flush(['rate', 'currency_id', 'company_id', 'name'])
            query = """SELECT c.id,
                COALESCE((SELECT r.rate FROM res_currency_rate r
                    WHERE r.currency_id = c.id AND r.name <= %s
                    AND (r.company_id IS NULL OR r.company_id = %s)
                    ORDER BY r.company_id, r.name DESC
                    LIMIT 1), 1.0) AS rate
                    FROM res_currency c
                WHERE c.id = %s"""
            company_obj = self.env['res.company'].browse(self.env.company.id)
            self._cr.execute(query, (date, company_obj.id, currency))
            currency_rates = dict(self._cr.fetchall())
            rate = currency_rates.get(currency) or 1.0
            self.currency_rate = 1 / rate if rate > 0 else 1


    @api.depends('currency_id', 'company_id', 'payment_has_exchange_rate','journal_id')
    def _compute_payment_exchange_allow(self):
        self.payment_exchange_allow_ok = False
        if self.currency_id != self.journal_id.company_id.currency_id:
            self.payment_exchange_allow_ok = True

    @api.onchange('payment_has_exchange_rate')
    def _onchange_payment_has_exchange_rate(self):
        if not self.payment_has_exchange_rate:
            self.payment_exchange_rate = 1

    @api.onchange('journal_id', 'payment_exchange_rate')
    def _compute_amount_signed(self):
        for payment in self:
            company_currency = self.env.company.currency_id
            journal_currency = payment.journal_id.currency_id or company_currency
            if payment.journal_id and payment.journal_id.currency_id:
                for advance in payment.advance_ids:
                    if payment.journal_id.currency_id != advance.currency_signed_id:
                        if advance.currency_signed_id.name == 'COP':
                            """anticipo en pesos para pagar en otra moneda"""
                            advance.amount_signed = advance.amount_original
                            advance.currency_signed_id = journal_currency
                            if payment.payment_has_exchange_rate and payment.payment_exchange_rate > 1:
                                advance.amount = advance.amount_original / payment.payment_exchange_rate
                            else:
                                advance.amount = advance.amount_original / payment.currency_rate
                        else:
                            """anticipo en otra moneda para pagar en pesos"""
                            advance.amount = advance.amount_original
                            advance.currency_id = journal_currency
                            if payment.payment_has_exchange_rate and payment.payment_exchange_rate > 1:
                                advance.amount_signed = advance.amount_original * payment.payment_exchange_rate
                            else:
                                date = self._context.get('date') or datetime.today()
                                self.env['res.currency.rate'].flush(['rate', 'currency_id', 'company_id', 'name'])
                                query = """SELECT c.id,
                                    COALESCE((SELECT r.rate FROM res_currency_rate r
                                        WHERE r.currency_id = c.id AND r.name <= %s
                                        AND (r.company_id IS NULL OR r.company_id = %s)
                                        ORDER BY r.company_id, r.name DESC
                                        LIMIT 1), 1.0) AS rate
                                        FROM res_currency c
                                    WHERE c.id = %s"""
                                company_obj = self.env['res.company'].browse(self.env.company.id)
                                self._cr.execute(query, (date, company_obj.id, advance.currency_signed_id.id))
                                currency_rates = dict(self._cr.fetchall())
                                rate = currency_rates.get(advance.currency_signed_id.id) or 1.0
                                currency_rate = 1 / rate if rate > 0 else 1
                                advance.amount_signed = advance.amount_original * currency_rate
                    elif payment.journal_id.currency_id.name != 'COP' and advance.currency_signed_id.name != 'COP':
                        advance.amount = advance.amount_original
                        advance.currency_id = company_currency
                        if payment.payment_has_exchange_rate and payment.payment_exchange_rate > 1:
                            advance.amount_signed = advance.amount_original * payment.payment_exchange_rate
                        else:
                            date = self._context.get('date') or datetime.today()
                            self.env['res.currency.rate'].flush(['rate', 'currency_id', 'company_id', 'name'])
                            query = """SELECT c.id,
                                COALESCE((SELECT r.rate FROM res_currency_rate r
                                    WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                                    ORDER BY r.company_id, r.name DESC
                                    LIMIT 1), 1.0) AS rate
                                    FROM res_currency c
                                WHERE c.id = %s"""
                            company_obj = self.env['res.company'].browse(self.env.company.id)
                            self._cr.execute(query, (date, company_obj.id, advance.currency_signed_id.id))
                            currency_rates = dict(self._cr.fetchall())
                            rate = currency_rates.get(advance.currency_signed_id.id) or 1.0
                            currency_rate = 1 / rate if rate > 0 else 1
                            advance.amount_signed = advance.amount_original * currency_rate

                payment.currency_id = payment.journal_id.currency_id
                payment.amount = 0
                payment.amount_signed = 0
                for advance in payment.advance_ids:
                    payment.amount += advance.amount
                    payment.amount_signed += advance.amount_signed


    @api.depends('journal_id')
    def _compute_currency_id(self):
        for wizard in self:
            wizard.currency_id = wizard.journal_id.currency_id or wizard.company_id.currency_id


    @api.depends('company_id', 'currency_id', 'payment_date','amount_signed')
    def _compute_amount(self):
        for wizard in self:
            wizard.amount = 0
            wizard.amount_signed = 0
            for advance in wizard.advance_ids:
                wizard.amount += advance.amount
                wizard.amount_signed += advance.amount_signed


    @api.model
    def default_get(self, fields_list):
        res = {}
        #advance_line_ids = self.env['account.advance.payment'].browse(self._context.get('active_ids', []))
        advance_line_ids = self.env['account.advance.payment'].search([
            ('id', 'in', self._context.get('active_ids')),
        ], order='supplier_id')
        line_list = []
        count = 0
        for advance in advance_line_ids:
            if not count:
                payment_has_exchange_rate = advance.payment_has_exchange_rate
                payment_exchange_rate = advance.payment_exchange_rate
            if advance.state != 'processed':
                raise UserError("Solo puede registrar pago de anticipos que esten Aprobados por el director y el financiero correspondiente.")
            if advance.payment_id and advance.payment_id.state == 'posted':
                raise UserError("El anticipo %s ya tiene un pago asociado y que se encuentra en estado %s." % (advance.name. advance_id.payment_id.state))
            line_list.append((0,0,{
				'wizard_id' : self.id,
                'account_advance_payment_id' : advance.id,
				'account_advance_payment_name' : advance.id,
                'amount' : advance.amount,
                'amount_original' : advance.amount,
                'amount_signed' : advance.amount_signed,
                'currency_id': self.env.company.currency_id.id,
                'currency_signed_id': advance.currency_id.id,
				'supplier_id' : advance.supplier_id.id,
				'beneficiary_id' : advance.beneficiary_id.id,
                'date_request': advance.date_request,
			}))
            count+=1
        res.update({
            #'currency_id': currency_id,
            'payment_has_exchange_rate': payment_has_exchange_rate,
            'payment_exchange_rate': payment_exchange_rate,
            'advance_ids': line_list
        })

        return res

    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------

    def _create_payment_vals_from_wizard(self, 
        supplier_id,
        amount_total,
        amount_total_signed,
        account_advance_id,
        currency_id):
        currency_rate = 1
        payment_has_exchange_rate = False

        if self.currency_id.id != self.env.company.currency_id.id:
            if self.payment_has_exchange_rate and self.payment_exchange_rate > 1:
                currency_rate = self.payment_exchange_rate
                payment_has_exchange_rate = True
            else:
                currency_rate = self.currency_rate
        payment_vals = {
            'date': self.payment_date,
            'amount': amount_total,
            'payment_type': self.payment_type,
            'partner_type': self.partner_type,
            'ref': self.communication,
            'journal_id': self.journal_id.id,
            'currency_id': currency_id,
            'currency_rate': currency_rate,
            'partner_id': supplier_id,
            'destination_account_id': account_advance_id,
            'payment_has_exchange_rate': payment_has_exchange_rate,
            'payment_exchange_rate': currency_rate,
            'payment_method_id': 2,
        }

        return payment_vals


    def _create_move_vals_from_wizard(self,
        new_payment,
        supplier_id,
        amount_total_signed,
        amount_total,
        account_advance_id,
        advance_amount_array):
        supplier_obj = self.env['res.partner'].browse(supplier_id)
        line_vals = []
        line_vals.append((0, 0, {
            'name': 'Pago a proveedor $ %s - \t%s - %s' % (amount_total, supplier_obj.name, self.payment_date),
            'date_maturity': self.payment_date, 
            'amount_currency': amount_total*-1, 
            'currency_id': self.currency_id.id, 
            'debit': 0.0, 
            'credit': amount_total_signed, 
            'partner_id': supplier_id, 
            'account_id': self.journal_id.suspense_account_id.id,
        }))
        for debit in advance_amount_array:
            line_vals.append(
                (0, 0, {
                    'name': 'Pago a proveedor $ %s - \t%s - %s' % (amount_total, supplier_obj.name, self.payment_date),
                    'date_maturity': self.payment_date, 
                    'amount_currency': amount_total, 
                    'currency_id': self.currency_id.id, 
                    'debit': debit, 
                    'credit': 0.0, 
                    'partner_id': supplier_id, 
                    'account_id': account_advance_id,
                })
            )
        new_payment.move_id.line_ids.unlink()
        new_payment.move_id.write({'line_ids': line_vals})


    def _post_payments(self, to_process, edit_mode=False):
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
        payments.action_post()


    def advance_update_with_payment(self, advance_array, new_payment_id):
        advance_update_ids = self.env['account.advance.payment'].search([('id', 'in', advance_array)])
        for advance_update in advance_update_ids:
            advance_update.write({
                'payment_id': new_payment_id,
                'state': 'posted'
            })


    def _create_payments_group(self):
        self.ensure_one()
        partner_ctl = False
        advance_ctl = False
        advance_array = []
        advance_amount_array = []
        new_payment = None
        amount_total = 0
        amount_total_signed = 0
        count = 0
        payment_vals = []
        payment_obj = self.env['account.payment']
        total_advances = len(self.advance_ids)
        for advance in self.advance_ids:
            count += 1
            advance_id = self.env['account.advance.payment'].browse(advance.account_advance_payment_id)
            if self.payment_has_exchange_rate and self.payment_exchange_rate > 1:
                advance_id.write({
                    'payment_has_exchange_rate': True,
                    'payment_exchange_rate': self.payment_exchange_rate
                })
            else:
                advance_id.write({
                    'payment_has_exchange_rate': False,
                    'payment_exchange_rate': 0,
                    'currency_rate': self.currency_rate
                })
            if not partner_ctl:
                _logger.error('ingresando al primer anticipo')
                partner_ctl = advance.supplier_id.id
                advance_ctl = advance_id.id
                advance_array.append(advance_id.id)
                advance_amount_array.append(advance.amount_signed)
                amount_total += advance.amount
                amount_total_signed += advance.amount_signed or advance.amount
                if len(self.advance_ids) == 1:
                    payment_vals = self._create_payment_vals_from_wizard(
                        advance.supplier_id.id,
                        amount_total,
                        amount_total_signed,
                        advance_id.account_advance_id.id,
                        advance_id.currency_id.id
                    )
                    new_payment = payment_obj.create(payment_vals)
                    self._create_move_vals_from_wizard(
                        new_payment,
                        advance.supplier_id.id,
                        amount_total_signed,
                        advance_id.account_advance_id.id,
                        advance_amount_array
                    )
                    new_payment.action_post()
                    advance_id.write({
                        'payment_id': new_payment.id,
                        'state': 'posted'
                    })
            elif advance.supplier_id.id != partner_ctl and partner_ctl:
                payment_vals = self._create_payment_vals_from_wizard(
                    self.env['res.partner'].browse(partner_ctl).id,
                    amount_total,
                    amount_total_signed,
                    self.env['account.advance.payment'].browse(advance_ctl).account_advance_id.id,
                    self.env['account.advance.payment'].browse(advance_ctl).currency_id.id
                )
                new_payment = payment_obj.create(payment_vals)
                self._create_move_vals_from_wizard(
                    new_payment,
                    self.env['res.partner'].browse(partner_ctl).id,
                    amount_total_signed,
                    self.env['account.advance.payment'].browse(advance_ctl).account_advance_id.id,
                    advance_amount_array
                )
                new_payment.action_post()
                self.advance_update_with_payment(advance_array, new_payment.id)
                advance_array = []
                advance_amount_array = []
                advance_array.append(advance_id.id)
                advance_amount_array.append(advance.amount_signed)
                amount_total = advance.amount
                amount_total_signed = advance.amount_signed or advance.amount
                partner_ctl = advance.supplier_id.id
                advance_ctl = advance_id.id
                if count == total_advances:
                    payment_vals = self._create_payment_vals_from_wizard(
                        advance.supplier_id.id,
                        amount_total,
                        amount_total_signed,
                        advance_id.account_advance_id.id,
                        advance_id.currency_id.id
                    )
                    new_payment = payment_obj.create(payment_vals)
                    self._create_move_vals_from_wizard(
                        new_payment,
                        advance.supplier_id.id,
                        amount_total_signed,
                        self.env['account.advance.payment'].browse(advance_ctl).account_advance_id.id,
                        advance_amount_array
                    )
                    new_payment.action_post()
                    self.advance_update_with_payment(advance_array, new_payment.id)
            else :
                amount_total += advance.amount
                amount_total_signed += advance.amount_signed or advance.amount
                advance_array.append(advance_id.id)
                advance_amount_array.append(advance.amount_signed)
                partner_ctl = advance.supplier_id.id
                advance_ctl = advance_id.id
                if count == total_advances:
                    payment_vals = self._create_payment_vals_from_wizard(
                        advance.supplier_id.id,
                        amount_total,
                        amount_total_signed,
                        advance_id.account_advance_id.id,
                        advance_id.currency_id.id
                    )
                    new_payment = payment_obj.create(payment_vals)
                    self._create_move_vals_from_wizard(
                        new_payment,
                        advance.supplier_id.id,
                        amount_total_signed,
                        advance_id.account_advance_id.id,
                        advance_amount_array
                    )
                    new_payment.action_post()
                    self.advance_update_with_payment(advance_array, new_payment.id)


    def _create_payments(self):
        self.ensure_one()
        partner_ctl = False
        advance_ctl = False
        advance_array = []
        advance_amount_array = []
        new_payment = None
        amount_total = 0
        amount_total_signed = 0
        count = 0
        payment_vals = []
        payment_obj = self.env['account.payment']
        for advance in self.advance_ids:
            count += 1
            advance_id = self.env['account.advance.payment'].browse(advance.account_advance_payment_id)
            if self.payment_has_exchange_rate and self.payment_exchange_rate > 1:
                advance_id.write({
                    'payment_has_exchange_rate': True,
                    'payment_exchange_rate': self.payment_exchange_rate
                })
            else:
                advance_id.write({
                    'payment_has_exchange_rate': False,
                    'payment_exchange_rate': 0,
                    'currency_rate': self.currency_rate
                })
            advance_id.write({
                'amount': advance.amount,
                'amount_signed': advance.amount_signed
            })
            advance_array = []
            advance_amount_array = []
            advance_array.append(advance_id.id)
            advance_amount_array.append(advance.amount_signed)
            amount_total = advance.amount
            amount_total_signed = advance.amount_signed or advance.amount
            payment_vals = self._create_payment_vals_from_wizard(
                advance.supplier_id.id,
                amount_total,
                amount_total_signed,
                advance_id.account_advance_id.id,
                #advance_id.currency_id.id
                self.currency_id.id
            )
            new_payment = payment_obj.create(payment_vals)
            self._create_move_vals_from_wizard(
                new_payment,
                advance.supplier_id.id,
                amount_total_signed,
                amount_total,
                advance_id.account_advance_id.id,
                advance_amount_array
            )
            new_payment.action_post()
            advance_id.write({
                'payment_id': new_payment.id,
                'state': 'posted'
            })


    def action_create_payments(self):
        if self.payment_group:
            self._create_payments_group()
        else:
            self._create_payments()


class AccountAdvancePaymentRegister(models.TransientModel):
    _name = 'account.advance.payment.register.line'

    wizard_id = fields.Many2one('account.advance.payment.register',string='Wizard ID')
    account_advance_payment_id = fields.Integer(string="Anticipo", invisible="1")
    account_advance_payment_name = fields.Many2one('account.advance.payment', string="Anticipo")
    currency_id = fields.Many2one('res.currency', string='Moneda Local')
    currency_signed_id = fields.Many2one('res.currency', string='Moneda Anticipo')
    amount = fields.Float('Valor Anticipo')
    amount_original = fields.Float('Valor Original Anticipo')
    amount_signed = fields.Float('Valor Moneda Local')
    supplier_id = fields.Many2one('res.partner', string='Proveedor')
    beneficiary_id = fields.Many2one('res.partner', string='Beneficiario')
    date_request = fields.Date('Fecha Solicitud')