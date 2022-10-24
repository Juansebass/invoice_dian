# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
from odoo.tools import float_compare
from datetime import datetime
from collections import defaultdict

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'out_receipt': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
    'in_receipt': 'supplier',
}
import logging

_logger = logging.getLogger(__name__)


class AccountPayment(models.Model):
    _inherit = "account.payment"

    state = fields.Selection(related="move_id.state", store=True)
    payment_date = fields.Date(related="move_id.date", store=True)
    payment_has_exchange_rate = fields.Boolean('Aplicar TRM por documento')
    payment_exchange_rate = fields.Float('TRM de este pago', default=1)
    payment_exchange_allow_ok = fields.Boolean('Permitir TRM por documento', compute="_compute_payment_exchange_allow")
    currency_rate = fields.Float(
        "TRM Nativa",
        compute='_compute_currency_rate', 
        compute_sudo=True,
        store=True,
        digits=(12, 6),
        readonly=True,
        help='TRM aplicada por Odoo nativamente, definida en la moneda de la empresa'
    )
    company_currency_id = fields.Many2one(related='journal_id.company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    amount_signed = fields.Monetary(
        string='Moneda Local',
        store=True,
        readonly=True,
        compute='_compute_amount_signed',
        currency_field='company_currency_id'
    )
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account',required=False)
    full_reconcile_ids = fields.One2many('account.full.reconcile',
                                         compute="_compute_full_reconcile_ids",
                                         string="Conciliaciones", 
                                         copy=False, 
                                         index=True, 
                                         readonly=True)


    @api.model
    def _compute_full_reconcile_ids(self):
        for rec in self:
            if rec.move_id:
                full_reconcile_ids = []
                rec.full_reconcile_ids = None
                for line in rec.move_id.line_ids:
                    if line.full_reconcile_id:
                        full_reconcile_ids.append((4, line.full_reconcile_id.id))
                if full_reconcile_ids:
                    rec.full_reconcile_ids = full_reconcile_ids

    @api.model
    def default_get(self, default_fields):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        active_model = self._context.get('active_model')
        if active_model == 'account.move':
            invoices = self.env['account.move'].browse(active_ids).filtered(lambda move: move.is_invoice(include_receipts=True))
            if any(invoice.amount_residual_signed == 0 for invoice in invoices):
                raise UserError(_("You can only register payments for invoices with residual"))
        res = super(AccountPayment, self).default_get(default_fields)

        return res


    @api.depends('partner_bank_id', 'amount', 'ref', 'currency_id', 'journal_id', 'move_id.state',
                 'payment_method_id', 'payment_type')
    def _compute_qr_code(self):
        for pay in self:
            if pay.state in ('draft', 'posted') \
                and pay.partner_bank_id \
                and pay.payment_method_id.code == 'manual' \
                and pay.payment_type == 'outbound' \
                and pay.currency_id:
                if pay.partner_bank_id:
                    #qr_code = pay.partner_bank_id.build_qr_code_base64(pay.amount, pay.ref, pay.ref, pay.currency_id, pay.partner_id)
                    """TODO:Modificado por que genera un error al editar la cuentas de banco del tercero"""
                    qr_code = None
                else:
                    qr_code = None

                if qr_code:
                    pay.qr_code = '''
                        <br/>
                        <img class="border border-dark rounded" src="{qr_code}"/>
                        <br/>
                        <strong class="text-center">{txt}</strong>
                        '''.format(txt = _('Scan me with your banking app.'),
                                   qr_code = qr_code)
                    continue

            pay.qr_code = None


    @api.depends('currency_id', 'company_id', 'payment_has_exchange_rate','journal_id')
    def _compute_payment_exchange_allow(self):
        self.payment_exchange_allow_ok = False
        if self.currency_id != self.journal_id.company_id.currency_id:
            self.payment_exchange_allow_ok = True

    @api.onchange('payment_has_exchange_rate')
    def _onchange_payment_has_exchange_rate(self):
        if not self.payment_has_exchange_rate:
            self.payment_exchange_rate = 1

    @api.depends(
        'journal_id',
        'payment_date',
        'company_id',
        'amount_signed',
        'amount',
        'payment_has_exchange_rate',
        'payment_exchange_rate',
        'currency_id')
    def _compute_amount_signed(self):
        for payment in self:
            amount = payment.amount
            company_currency = payment.journal_id.company_id.currency_id or self.env.company.currency_id
            journal_currency = payment.journal_id.currency_id or company_currency
            payment_currency = payment.currency_id or company_currency
            if payment_currency == journal_currency:
                payment.amount_signed = amount
                continue
            if payment.payment_has_exchange_rate and payment.payment_exchange_rate > 1:
                payment.amount_signed = payment_currency._convert_per_document(
                    payment.amount, journal_currency, payment.journal_id.company_id if payment.journal_id else self.env.company,
                    payment.payment_date or fields.Date.today(),payment.payment_exchange_rate)
            else:
                payment.amount_signed = payment_currency._convert(
                    payment.amount, journal_currency, payment.journal_id.company_id if payment.journal_id else self.env.company,
                    payment.payment_date or fields.Date.today())


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


    def action_register_payment(self):
        res = super(AccountPayment, self).action_register_payment()
        active_ids = self.env.context.get('active_ids')
        if not active_ids:
            return ''
        currency_cont = len(self.env['account.move'].read_group([('id', 'in', active_ids)], fields=['id'], groupby=['currency_id']))
        self.env.context = dict(self.env.context)
        self.env.context.update({'message_many_currencies': False})
        if currency_cont > 1:
            self.env.context.update({'message_many_currencies': True})
        res.update({'context': self.env.context})
        return res


    def _prepare_move_line_default_vals(self, write_off_line_vals=None):
        ''' Prepare the dictionary to create the default account.move.lines for the current payment.
        :param write_off_line_vals: Optional dictionary to create a write-off account.move.line easily containing:
            * amount:       The amount to be added to the counterpart amount.
            * name:         The label to set on the line.
            * account_id:   The account on which create the write-off.
        :return: A list of python dictionary to be passed to the account.move.line's 'create' method.
        '''
        self.ensure_one()
        write_off_line_vals = write_off_line_vals or {}
        if not self.journal_id.inbound_payment_method_line_ids or not self.journal_id.outbound_payment_method_line_ids:
            raise UserError(_(
                "You can't create a new payment without an outstanding payments/receipts account set on the %s journal.",
                self.journal_id.display_name))

        # Compute amounts.
        write_off_amount_currency = write_off_line_vals.get('amount', 0.0)

        if self.payment_type == 'inbound':
            # Receive money.
            liquidity_amount_currency = self.amount
        elif self.payment_type == 'outbound':
            # Send money.
            liquidity_amount_currency = -self.amount
            write_off_amount_currency *= -1
        else:
            liquidity_amount_currency = write_off_amount_currency = 0.0

        if self.payment_has_exchange_rate and self.payment_exchange_rate > 1:
            write_off_balance = self.currency_id._convert_per_document(
                write_off_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
                self.payment_exchange_rate,
            )
            liquidity_balance = self.currency_id._convert_per_document(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
                self.payment_exchange_rate,
            )
        else:
            write_off_balance = self.currency_id._convert(
                write_off_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
            liquidity_balance = self.currency_id._convert(
                liquidity_amount_currency,
                self.company_id.currency_id,
                self.company_id,
                self.date,
            )
        counterpart_amount_currency = -liquidity_amount_currency - write_off_amount_currency
        counterpart_balance = -liquidity_balance - write_off_balance
        currency_id = self.currency_id.id

        if self.is_internal_transfer:
            if self.payment_type == 'inbound':
                liquidity_line_name = _('Transfer to %s', self.journal_id.name)
            else: # payment.payment_type == 'outbound':
                liquidity_line_name = _('Transfer from %s', self.journal_id.name)
        else:
            liquidity_line_name = self.payment_reference

        # Compute a default label to set on the journal items.

        payment_display_name = {
            'outbound-customer': _("Customer Reimbursement"),
            'inbound-customer': _("Customer Payment"),
            'outbound-supplier': _("Vendor Payment"),
            'inbound-supplier': _("Vendor Reimbursement"),
        }

        default_line_name = self.env['account.move.line']._get_default_line_name(
            _("Internal Transfer") if self.is_internal_transfer else payment_display_name['%s-%s' % (self.payment_type, self.partner_type)],
            self.amount,
            self.currency_id,
            self.date,
            partner=self.
            partner_id,
        )
        payment_inbound_account = self.journal_id.inbound_payment_method_line_ids.filtered(
            lambda x: x.payment_method_id == self.payment_method_id).mapped('payment_account_id')
        payment_outbound_account = self.journal_id.outbound_payment_method_line_ids.filtered(
            lambda x: x.payment_method_id == self.payment_method_id).mapped('payment_account_id')

        line_vals_list = [
            # Liquidity line.
            {
                'name': liquidity_line_name or default_line_name,
                'date_maturity': self.date,
                'amount_currency': liquidity_amount_currency,
                'currency_id': currency_id,
                'debit': liquidity_balance if liquidity_balance > 0.0 else 0.0,
                'credit': -liquidity_balance if liquidity_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': payment_outbound_account.id if liquidity_balance < 0.0 else payment_inbound_account.id,
            },
            # Receivable / Payable.
            {
                'name': self.payment_reference or default_line_name,
                'date_maturity': self.date,
                'amount_currency': counterpart_amount_currency,
                'currency_id': currency_id,
                'debit': counterpart_balance if counterpart_balance > 0.0 else 0.0,
                'credit': -counterpart_balance if counterpart_balance < 0.0 else 0.0,
                'partner_id': self.partner_id.id,
                'account_id': self.destination_account_id.id,
            },
        ]
        for rec in self.currency_id:
            if not rec.is_zero(write_off_amount_currency):
                # Write-off line.
                line_vals_list.append({
                    'name': write_off_line_vals.get('name') or default_line_name,
                    'amount_currency': write_off_amount_currency,
                    'currency_id': currency_id,
                    'debit': write_off_balance if write_off_balance > 0.0 else 0.0,
                    'credit': -write_off_balance if write_off_balance < 0.0 else 0.0,
                    'partner_id': self.partner_id.id,
                    'account_id': write_off_line_vals.get('account_id'),
                })
        return line_vals_list


    def _prepare_payment_moves(self):
        res = super(AccountPayment, self)._prepare_payment_moves()
        all_move_vals = []
        for payment in self:
            if payment.payment_has_exchange_rate and payment.payment_exchange_rate > 1:
                company_currency = payment.company_id.currency_id
                move_names = payment.move_name.split(payment._get_move_name_transfer_separator()) if payment.move_name else None

                # Compute amounts.
                write_off_amount = payment.payment_difference_handling == 'reconcile' and -payment.payment_difference or 0.0
                if payment.payment_type in ('outbound', 'transfer'):
                    counterpart_amount = payment.amount
                    liquidity_line_account = payment.journal_id.default_debit_account_id
                else:
                    counterpart_amount = -payment.amount
                    liquidity_line_account = payment.journal_id.default_credit_account_id

                # Manage currency.
                if payment.currency_id == company_currency:
                    # Single-currency.
                    balance = counterpart_amount
                    write_off_balance = write_off_amount
                    counterpart_amount = write_off_amount = 0.0
                    currency_id = False
                else:
                    # Multi-currencies.
                    balance = payment.currency_id._convert_per_document(
                        counterpart_amount,
                        company_currency,
                        payment.company_id,
                        payment.payment_date,
                        payment.payment_exchange_rate
                    )
                    write_off_balance = payment.currency_id._convert_per_document(
                        write_off_amount,
                        company_currency,
                        payment.company_id,
                        payment.payment_date,
                        payment.payment_exchange_rate
                    )
                    currency_id = payment.currency_id.id

                # Manage custom currency on journal for liquidity line.
                if payment.journal_id.currency_id and payment.currency_id != payment.journal_id.currency_id:
                    # Custom currency on journal.
                    if payment.journal_id.currency_id == company_currency:
                        # Single-currency
                        liquidity_line_currency_id = False
                    else:
                        liquidity_line_currency_id = payment.journal_id.currency_id.id
                    liquidity_amount = company_currency._convert_per_document(
                        balance, payment.journal_id.currency_id, payment.company_id, payment.payment_date, payment.payment_exchange_rate)
                else:
                    # Use the payment currency.
                    liquidity_line_currency_id = currency_id
                    liquidity_amount = counterpart_amount

                # Compute 'name' to be used in receivable/payable line.
                rec_pay_line_name = ''
                if payment.payment_type == 'transfer':
                    rec_pay_line_name = payment.name
                else:
                    if payment.partner_type == 'customer':
                        if payment.payment_type == 'inbound':
                            rec_pay_line_name += _("Customer Payment")
                        elif payment.payment_type == 'outbound':
                            rec_pay_line_name += _("Customer Credit Note")
                    elif payment.partner_type == 'supplier':
                        if payment.payment_type == 'inbound':
                            rec_pay_line_name += _("Vendor Credit Note")
                        elif payment.payment_type == 'outbound':
                            rec_pay_line_name += _("Vendor Payment")
                    if payment.invoice_ids:
                        rec_pay_line_name += ': %s' % ', '.join(payment.invoice_ids.mapped('name'))

                # Compute 'name' to be used in liquidity line.
                if payment.payment_type == 'transfer':
                    liquidity_line_name = _('Transfer to %s') % payment.destination_journal_id.name
                else:
                    liquidity_line_name = payment.name

                # ==== 'inbound' / 'outbound' ====

                move_vals = {
                    'date': payment.payment_date,
                    'ref': payment.communication,
                    'journal_id': payment.journal_id.id,
                    'currency_id': payment.journal_id.currency_id.id or payment.company_id.currency_id.id,
                    'partner_id': payment.partner_id.id,
                    'line_ids': [
                        # Receivable / Payable / Transfer line.
                        (0, 0, {
                            'name': rec_pay_line_name,
                            'amount_currency': counterpart_amount + write_off_amount if currency_id else 0.0,
                            'currency_id': currency_id,
                            'debit': balance + write_off_balance > 0.0 and balance + write_off_balance or 0.0,
                            'credit': balance + write_off_balance < 0.0 and -balance - write_off_balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': payment.destination_account_id.id,
                            'payment_id': payment.id,
                            'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else '',
                        }),
                        # Liquidity line.
                        (0, 0, {
                            'name': liquidity_line_name,
                            'amount_currency': -liquidity_amount if liquidity_line_currency_id else 0.0,
                            'currency_id': liquidity_line_currency_id,
                            'debit': balance < 0.0 and -balance or 0.0,
                            'credit': balance > 0.0 and balance or 0.0,
                            'date_maturity': payment.payment_date,
                            'partner_id': payment.partner_id.commercial_partner_id.id,
                            'account_id': liquidity_line_account.id,
                            'payment_id': payment.id,
                            'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else '',
                        }),
                    ],
                }
                if write_off_balance:
                    # Write-off line.
                    move_vals['line_ids'].append((0, 0, {
                        'name': payment.writeoff_label,
                        'amount_currency': -write_off_amount,
                        'currency_id': currency_id,
                        'debit': write_off_balance < 0.0 and -write_off_balance or 0.0,
                        'credit': write_off_balance > 0.0 and write_off_balance or 0.0,
                        'date_maturity': payment.payment_date,
                        'partner_id': payment.partner_id.commercial_partner_id.id,
                        'account_id': payment.writeoff_account_id.id,
                        'payment_id': payment.id,
                        'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else '',
                    }))

                if move_names:
                    move_vals['name'] = move_names[0]

                all_move_vals.append(move_vals)

                # ==== 'transfer' ====
                if payment.payment_type == 'transfer':
                    journal = payment.destination_journal_id

                    # Manage custom currency on journal for liquidity line.
                    if journal.currency_id and payment.currency_id != journal.currency_id:
                        # Custom currency on journal.
                        liquidity_line_currency_id = journal.currency_id.id
                        transfer_amount = company_currency._convert_per_document(
                            balance,
                            journal.currency_id,
                            payment.company_id,
                            payment.payment_date,
                            payment.payment_exchange_rate
                        )
                    else:
                        # Use the payment currency.
                        liquidity_line_currency_id = currency_id
                        transfer_amount = counterpart_amount

                    transfer_move_vals = {
                        'date': payment.payment_date,
                        'ref': payment.communication,
                        'partner_id': payment.partner_id.id,
                        'journal_id': payment.destination_journal_id.id,
                        'line_ids': [
                            # Transfer debit line.
                            (0, 0, {
                                'name': payment.name,
                                'amount_currency': -counterpart_amount if currency_id else 0.0,
                                'currency_id': currency_id,
                                'debit': balance < 0.0 and -balance or 0.0,
                                'credit': balance > 0.0 and balance or 0.0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.company_id.transfer_account_id.id,
                                'payment_id': payment.id,
                                'analytic_account_id': self.analytic_account_id if self.analytic_account_id else '',
                            }),
                            # Liquidity credit line.
                            (0, 0, {
                                'name': _('Transfer from %s') % payment.journal_id.name,
                                'amount_currency': transfer_amount if liquidity_line_currency_id else 0.0,
                                'currency_id': liquidity_line_currency_id,
                                'debit': balance > 0.0 and balance or 0.0,
                                'credit': balance < 0.0 and -balance or 0.0,
                                'date_maturity': payment.payment_date,
                                'partner_id': payment.partner_id.commercial_partner_id.id,
                                'account_id': payment.destination_journal_id.default_credit_account_id.id,
                                'payment_id': payment.id,
                                'analytic_account_id': self.analytic_account_id if self.analytic_account_id else '',
                            }),
                        ],
                    }

                    if move_names and len(move_names) == 2:
                        transfer_move_vals['name'] = move_names[1]

                    all_move_vals.append(transfer_move_vals)
                return all_move_vals
            else:
                return res


class payment_register(models.TransientModel):
    _inherit = 'account.payment.register'

    message_amount_exceeded = fields.Boolean(string='Monto Excedido', compute='_get_context_message_amount_exceeded')
    advance_ok = fields.Boolean('Anticipo')
    payment_has_exchange_rate = fields.Boolean('Aplicar TRM por documento')
    payment_exchange_rate = fields.Float('TRM del documento', default=1)


    @api.depends('amount')
    def _get_context_message_amount_exceeded(self):
        self.message_amount_exceeded = False
        if 'message_amount_exceeded' in self.env.context and dict(self.env.context)['message_amount_exceeded'] == True:
            self.message_amount_exceeded = True 


    @api.model
    def default_get(self, fields):
        rec = super(payment_register, self).default_get(fields)
        active_ids = self._context.get('active_ids')
        if not active_ids:
            return rec
        invoices = self.env['account.move'].browse(active_ids)
        unique_invoice_currency = None
        for invoice in invoices:
            if not unique_invoice_currency:
                unique_invoice_currency = invoice.currency_id
            if unique_invoice_currency != invoice.currency_id:
                raise Warning(_("La moneda de pago es diferente a la moneda de cualquiera de las facturas relacionadas."))
        return rec


    def _create_payment_vals_from_wizard(self):
        res = super(payment_register, self)._create_payment_vals_from_wizard()
        res.update({
            'x_studio_anticipo': self.advance_ok,
            'payment_has_exchange_rate': True,
            'payment_exchange_rate': self.payment_exchange_rate
        })

        return res


    def _create_payment_vals_from_batch(self, batch_result):
        res = super(payment_register, self)._create_payment_vals_from_batch(batch_result)
        res.update({
            'x_studio_anticipo': self.advance_ok,
            'payment_has_exchange_rate': True,
            'payment_exchange_rate': self.payment_exchange_rate
        })

        return res


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
