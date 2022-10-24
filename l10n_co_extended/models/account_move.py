# -*- coding: utf-8 -*-

from odoo import fields, models, api, _


class AccountMove(models.Model):
    _inherit = "account.move"


    refund_type = fields.Selection(
        [('debit', 'Debit Note'),
         ('credit', 'Credit Note')],
        index=True,
        string='Refund Type',
        tracking=True)

    invoice_has_exchange_rate = fields.Boolean('Aplicar TRM por documento')
    invoice_exchange_rate = fields.Float('TRM del documento', default=1)
    currency_rate_raw = fields.Float("TRM Actual", help="Native field calc from res currency rates")
    amount_total_exchange_rate = fields.Monetary(
        string='Total con TRM Aplicada',store=True, readonly=True, compute='_amount_all_with_exchange_rate', tracking=4)
    invoice_exchange_allow_ok = fields.Boolean('Allow Exchange Rate', compute="_compute_invoice_exchange_allow_ok")
    is_fiscal_move = fields.Boolean(string="Movimiento de Contabilidad Fiscal")
    currency_exchange = fields.Boolean('Currency exchange', compute='_get_currency_exchange', 
        help="It is 'True if created in the 'Mass Currency Exchange' process")


    @api.depends('invoice_has_exchange_rate','amount_total')
    def _amount_all_with_exchange_rate(self):
        for rec in self:
            amount_total_exchange_rate = 0.0
            if rec.invoice_has_exchange_rate and rec.invoice_exchange_rate > 1:
                amount_total_exchange_rate = rec.amount_total * rec.invoice_exchange_rate
            elif not rec.invoice_has_exchange_rate and rec.currency_rate_raw > 1:
                amount_total_exchange_rate = rec.amount_total * rec.currency_rate_raw

            rec.amount_total_exchange_rate = amount_total_exchange_rate


    @api.depends('currency_id', 'company_currency_id', 'company_id', 'invoice_has_exchange_rate')
    def _compute_invoice_exchange_allow_ok(self):
        self.invoice_exchange_allow_ok = False
        if self.currency_id != self.company_currency_id:
            self.invoice_exchange_allow_ok = True


    @api.onchange('invoice_exchange_rate')
    def _onchange_invoice_exchange_rate(self):
        if self.invoice_has_exchange_rate:
            currency = self.currency_id or self.company_id.currency_id
            self.amount_total_exchange_rate = self.amount_total * self.invoice_exchange_rate
            if self.is_invoice(include_receipts=True):
                for line in self._get_lines_onchange_currency():
                    line.currency_id = currency
                    line._onchange_currency()
            else:
                for line in self.line_ids:
                    line._onchange_currency()

            self._recompute_dynamic_lines(recompute_tax_base_amount=True)


    @api.onchange('invoice_has_exchange_rate')
    def _onchange_invoice_has_exchange_rate(self):
        if self.invoice_has_exchange_rate:
            self.amount_total_exchange_rate = self.amount_total * self.invoice_exchange_rate
        else:
            self.invoice_exchange_rate = 1
            self.amount_total_exchange_rate = self.amount_total * self.currency_rate_raw


    @api.onchange('currency_id')
    def _onchange_currency_id(self):
        if not self.currency_id:
            self.currency_rate_raw = 1
            self.invoice_has_exchange_rate = False
            self.invoice_exchange_rate = 1
            self.amount_total_exchange_rate = 0
        else:
            date = self.invoice_date or self._context.get('date') or self.date or datetime.today()
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
            self._cr.execute(query, (date, company_obj.id, self.currency_id.id))
            currency_rates = dict(self._cr.fetchall())
            rate = currency_rates.get(self.currency_id.id) or 1.0
            self.currency_rate_raw = 1 / rate if rate > 0 else 1
