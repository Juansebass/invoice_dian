# -*- coding: utf-8 -*-

import logging
from odoo import fields, models, api, _
from odoo.tools import float_compare
from datetime import datetime
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    account_advance_id = fields.Many2one('account.account', string='Cuenta de Anticipos')


class Employee(models.Model):
    _inherit = 'hr.employee'

    def _group_hr_expense_user_domain(self):
        group = self.env.ref('hr_expense.group_hr_expense_team_approver', raise_if_not_found=False)
        return [('groups_id', 'in', group.ids)] if group else []

    expense_treasury_id = fields.Many2one(
        'res.users', string='Financiero',
        domain=_group_hr_expense_user_domain,
        compute='_compute_expense_treasury', store=True, readonly=False)

    expense_manager_ids = fields.Many2many(
        'res.users', string='Anticipos Gasto',
        domain=_group_hr_expense_user_domain,store=True, readonly=False)


    @api.depends('parent_id')
    def _compute_expense_treasury(self):
        for employee in self:
            previous_manager = employee._origin.parent_id.user_id
            manager = employee.parent_id.user_id
            if manager and manager.has_group('hr_expense.group_hr_expense_user') and (employee.expense_treasury_id == previous_manager or not employee.expense_treasury_id):
                employee.expense_treasury_id = manager
            elif not employee.expense_treasury_id:
                employee.expense_treasury_id = False


class EmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    expense_manager_ids = fields.Many2many('res.users', readonly=True)
    expense_treasury_id = fields.Many2one('res.users', readonly=True)


class User(models.Model):
    _inherit = ['res.users']

    expense_manager_ids = fields.Many2many(related='employee_id.expense_manager_ids', readonly=False)
    expense_treasury_id = fields.Many2one(related='employee_id.expense_treasury_id', readonly=False)


class HrExpense(models.Model):
    _inherit = ['hr.expense']

    partner_id = fields.Many2one('res.partner', string='Tercero', required=True, tracking=True, states={'draft': [('readonly', False)]}, check_company=True)

    @api.model
    def create(self, vals):
        if 'account_id' not in vals and 'product_id' in vals:
            product_id = self.env['product.product'].browse(vals.get('product_id'))
            if product_id:
                account_id = product_id.product_tmpl_id._get_product_accounts()['expense']
                if account_id:
                    vals.update({
                        'account_id': account_id.id,
                    })
        res = super(HrExpense, self).create(vals)
        return res


    @api.depends('product_id', 'company_id')
    def _compute_from_product_id_company_id(self):
        for expense in self.filtered('product_id'):
            expense = expense.with_company(expense.company_id)
            expense.name = expense.name or expense.product_id.display_name
            if not expense.attachment_number or (expense.attachment_number and not expense.unit_amount):
                expense.unit_amount = expense.product_id.price_compute('standard_price')[expense.product_id.id]
            expense.product_uom_id = expense.product_id.uom_id
            expense.tax_ids = expense.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == expense.company_id)  # taxes only from the same company
            account = expense.product_id.product_tmpl_id._get_product_accounts()['expense']
            if account:
                expense.account_id = account



    """ Override"""
    def _get_account_move_line_values(self):
        move_line_values_by_expense = {}
        for expense in self:
            move_line_name = expense.partner_id.name + ': ' + expense.name.split('\n')[0][:64]
            account_src = expense._get_expense_account_source()
            account_dst = expense._get_expense_account_destination()
            account_date = expense.sheet_id.accounting_date or expense.date or fields.Date.context_today(expense)

            company_currency = expense.company_id.currency_id

            move_line_values = []
            unit_amount = expense.unit_amount or expense.total_amount
            quantity = expense.quantity if expense.unit_amount else 1
            taxes = expense.tax_ids.with_context(round=True).compute_all(unit_amount, expense.currency_id,quantity,expense.product_id)
            total_amount = 0.0
            total_amount_currency = 0.0
            partner_id = expense.employee_id.sudo().address_home_id.commercial_partner_id.id
            partner2_id = expense.partner_id.id

            # source move line
            balance = expense.currency_id._convert(taxes['total_excluded'], company_currency, expense.company_id, account_date)
            amount_currency = taxes['total_excluded']
            move_line_src = {
                'name': move_line_name,
                'quantity': expense.quantity or 1,
                'debit': balance if balance > 0 else 0,
                'credit': -balance if balance < 0 else 0,
                'amount_currency': amount_currency,
                'account_id': account_src.id,
                'product_id': expense.product_id.id,
                'product_uom_id': expense.product_uom_id.id,
                'analytic_account_id': expense.analytic_account_id.id,
                'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)],
                'expense_id': expense.id,
                'partner_id': partner2_id,
                'tax_ids': [(6, 0, expense.tax_ids.ids)],
                'tax_tag_ids': [(6, 0, taxes['base_tags'])],
                'currency_id': expense.currency_id.id,
            }
            move_line_values.append(move_line_src)
            total_amount -= balance
            total_amount_currency -= move_line_src['amount_currency']

            # taxes move lines
            for tax in taxes['taxes']:
                balance = expense.currency_id._convert(tax['amount'], company_currency, expense.company_id, account_date)
                amount_currency = tax['amount']

                if tax['tax_repartition_line_id']:
                    rep_ln = self.env['account.tax.repartition.line'].browse(tax['tax_repartition_line_id'])
                    base_amount = self.env['account.move']._get_base_amount_to_display(tax['base'], rep_ln)
                    base_amount = expense.currency_id._convert(base_amount, company_currency, expense.company_id, account_date)
                else:
                    base_amount = None

                move_line_tax_values = {
                    'name': tax['name'],
                    'quantity': 1,
                    'debit': balance if balance > 0 else 0,
                    'credit': -balance if balance < 0 else 0,
                    'amount_currency': amount_currency,
                    'account_id': tax['account_id'] or move_line_src['account_id'],
                    'tax_repartition_line_id': tax['tax_repartition_line_id'],
                    'tax_tag_ids': tax['tag_ids'],
                    'tax_base_amount': base_amount,
                    'expense_id': expense.id,
                    'partner_id': partner2_id,
                    'currency_id': expense.currency_id.id,
                    'analytic_account_id': expense.analytic_account_id.id if tax['analytic'] else False,
                    'analytic_tag_ids': [(6, 0, expense.analytic_tag_ids.ids)] if tax['analytic'] else False,
                }
                total_amount -= balance
                total_amount_currency -= move_line_tax_values['amount_currency']
                move_line_values.append(move_line_tax_values)

            # destination move line
            move_line_dst = {
                'name': move_line_name,
                'debit': total_amount > 0 and total_amount,
                'credit': total_amount < 0 and -total_amount,
                'account_id': account_dst,
                'date_maturity': account_date,
                'amount_currency': total_amount_currency,
                'currency_id': expense.currency_id.id,
                'expense_id': expense.id,
                'partner_id': partner_id,
            }
            move_line_values.append(move_line_dst)

            move_line_values_by_expense[expense.id] = move_line_values
        return move_line_values_by_expense


class AccountAdvancePayment(models.Model):
    _name = 'account.advance.payment'
    _inherit = [
        'mail.thread', 'mail.activity.mixin'
    ]
    _order = 'id desc'


    name = fields.Char(copy=False, required=True, readonly=True,
                       default=lambda self: ('Nuevo'), help="Número de Secuencia")
    user_id = fields.Many2one('res.users', string='Usuario', default=lambda self: self.env.uid, required=True)
    supplier_id = fields.Many2one('res.partner', string='Proveedor', required=True)
    beneficiary_id = fields.Many2one('res.partner', string='Beneficiario', required=True)
    account_advance_id = fields.Many2one('account.account', string='Cuenta Anticipos Proveedor', related='supplier_id.account_advance_id', readonly=True, required=True)
    currency_id = fields.Many2one('res.currency', string='Moneda', required=True)
    amount = fields.Float('Valor', required=True)
    date_request = fields.Date('Fecha Solicitud', required=True)
    purchase_order_id = fields.Many2one('purchase.order', string='Orden de Compra', copy=False)
    #purchase_import_id = fields.Many2one('purchase.imports', string='Importación', copy=False)
    note = fields.Text(string='Descripción', copy=False)
    payment_id = fields.Many2one('account.payment', string='Pago', copy=False, readonly=True)
    date_payment = fields.Date('Fecha de Pago', related='payment_id.move_id.date', readonly=True, copy=False)
    state = fields.Selection(
        [('draft', 'Borrador'),
         ('waiting_approval', 'Esperando Aprobación Director'),
         #('approved', 'Aprobado Director'),
         ('rejected', 'Rechazado Director'),
         ('waiting_approval2', 'Esperando Aprobación Financiero'),
         #('approved2', 'Aprobado Tesorería'),
         ('rejected2', 'Rechazado Financiero'),
         ('processed', 'Aprobado'),
         ('posted', 'Contabilizado'),
         ('cancel', 'Anulado'),],
        string='Estado',
        default='draft',
        track_visibility='onchange',
        readonly=True,
        required=True)
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
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
        readonly=True, store=True,
        help='Utility field to express amount currency')
    company_id = fields.Many2one('res.company', store=True, copy=False, default=lambda self: self.env.company)
    amount_signed = fields.Monetary(
        string='Moneda Local',
        store=True,
        readonly=False,
        #compute='_compute_amount_signed',
        currency_field='company_currency_id'
    )
    account_analytic_id = fields.Many2one('account.analytic.account', string='Centro de Costo')


    @api.model
    def default_get(self, fields_list):
        res = {}
        res.update({
            'user_id': self.env.uid,
            'name': 'Nuevo',
            'state': 'draft'
        })
        if self._context.get('default_supplier_id'):
            res.update({
                'supplier_id': self._context.get('default_supplier_id'),
            })
        if self._context.get('defautl_beneficiary_id'):
            res.update({
                'beneficiary_id': self._context.get('defautl_beneficiary_id'),
            })
        if self._context.get('default_purchase_order_id'):
            res.update({
                'purchase_order_id': self._context.get('default_purchase_order_id'),
            })
            #purchase_order_id = self.env['purchase.order'].browse(self._context.get('default_purchase_order_id'))
            #if purchase_order_id:
            #    res.update({
            #        'purchase_import_id': purchase_order_id.id,
            #   })
        if self._context.get('default_currency_id'):
            res.update({
                'currency_id': self._context.get('default_currency_id'),
            })
        return res

    @api.onchange('supplier_id')
    def _onchange_supplier_id(self):
        for rec in self:
            if not rec.beneficiary_id and rec.supplier_id:
                rec.beneficiary_id = rec.supplier_id

    """
    @api.onchange('purchase_import_id')
    def _onchange_purchase_import_id(self):
        for rec in self:
            if rec.purchase_import_id:
                purchase_order_id = self.env['purchase.order'].search([('purchase_import_id', '=', rec.purchase_import_id.id)])
                if purchase_order_id:
                    rec.purchase_order_id = purchase_order_id.id
    """

    """
    @api.onchange('purchase_order_id')
    def _onchange_purchase_order_id(self):
        for rec in self:
            if rec.purchase_order_id and rec.purchase_order_id.purchase_import_id:
                rec.purchase_import_id = rec.purchase_order_id.purchase_import_id.id
    """

    @api.depends('date_request', 'company_id','currency_id')
    def _compute_currency_rate(self):
        for advance in self:
            date = self._context.get('date') or datetime.today()
            company_currency = advance.company_id.currency_id or self.env.company.currency_id
            journal_currency = advance.currency_id or company_currency
            payment_currency = advance.currency_id or company_currency
            currency = advance.currency_id.id
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


    @api.depends('currency_id', 'company_id', 'payment_has_exchange_rate')
    def _compute_payment_exchange_allow(self):
        self.payment_exchange_allow_ok = False
        if self.currency_id != self.company_id.currency_id:
            self.payment_exchange_allow_ok = True

    @api.onchange('payment_has_exchange_rate')
    def _onchange_payment_has_exchange_rate(self):
        if not self.payment_has_exchange_rate:
            self.payment_exchange_rate = 1

    @api.onchange(
        'date_request',
        'company_id',
        #'amount_signed',
        'amount',
        'payment_has_exchange_rate',
        'payment_exchange_rate',
        'currency_id')
    #@api.depends(
    #    'date_request',
    #    'company_id',
        #'amount_signed',
    #    'amount',
    #    'payment_has_exchange_rate',
    #    'payment_exchange_rate',
    #    'currency_id')
    def _compute_amount_signed(self):
        for advance in self:
            amount = advance.amount
            amount_signed = 0.0
            currencies = set()
            company_currency = advance.company_id.currency_id or self.env.company.currency_id
            journal_currency = company_currency
            payment_currency = advance.currency_id or company_currency
            if payment_currency == journal_currency:
                advance.amount_signed = amount
                continue
            if advance.payment_has_exchange_rate and advance.payment_exchange_rate > 1:
                advance.amount_signed = payment_currency._convert_per_document(
                    advance.amount, journal_currency, advance.company_id or self.env.company,
                    advance.date_request or fields.Date.today(),advance.payment_exchange_rate)
            else:
                _logger.error('ingresando por el else')
                advance.amount_signed = payment_currency._convert(
                    advance.amount, journal_currency, advance.company_id or self.env.company,
                    advance.date_request or fields.Date.today())


    def action_cancel(self):
        for rec in self:
            if rec.state in ('waiting_approval','waiting_approval2','draft','processed'):
                rec.state = 'cancel'
            else:
                raise UserError(u'No es posible cancelar un anticipo en estado %s' % (rec.state))


    def action_confirmed(self):
        for rec in self:
            if rec.state in ('draft'):
                if rec.name == 'Nuevo':
                    rec.name = self.env['ir.sequence'].next_by_code('account.advance.payment') or 'Nuevo'       
                rec.state = 'waiting_approval'
            else:
                raise UserError(u'No es posible cancelar un anticipo en estado %s' % (rec.state))


    def action_approved(self):
        for rec in self:
            if rec.state in ('waiting_approval'):
                employee_id = self.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)])
                if not employee_id:
                    raise UserError(u'No existe un empleado asociado el usuario que creo el anticipo, por lo tanto el sistema de aprobaciones de anticipos no funciona. Consulte al administrador del sistema.')
                expense_manager_ids = employee_id.expense_manager_ids
                if not expense_manager_ids:
                    raise UserError(u'El empleado asociado al usuario que creo el anticipo no tiene definido un aprobador de tipo director. Consulte al administrador del sistema.')
                if self.env.uid not in expense_manager_ids.ids:
                    raise UserError(u'El usuario %s no tiene permitido aprobar este anticipo' % (self.env.user.name))
                else:
                    rec.state = 'waiting_approval2'
            elif rec.state in ('waiting_approval2'):
                employee_id = self.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)])
                if not employee_id:
                    raise UserError(u'No existe un empleado asociado el usuario que creo el anticipo, por lo tanto el sistema de aprobaciones de anticipos no funciona. Consulte al administrador del sistema.')
                expense_treasury_id = employee_id.expense_treasury_id
                if not expense_treasury_id:
                    raise UserError(u'El empleado asociado al usuario que creo el anticipo no tiene definido un aprobador de tipo tesorería. Consulte al administrador del sistema.')
                if self.env.uid != expense_treasury_id.id:
                    raise UserError(u'El usuario %s no tiene permitido aprobar este anticipo' % (self.env.user.name))
                else:
                    rec.state = 'processed'            
            else:
                raise UserError(u'No es posible cancelar un anticipo en estado %s' % (rec.state))


    def action_register_payment(self):
        ''' Open the account.payment.register wizard to pay the selected journal entries.
        :return: An action opening the account.advance.payment.register wizard.
        '''

        return {
            'name': _('Registrar Pago de Anticipo'),
            'res_model': 'account.advance.payment.register',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.advance.payment',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }


    def action_rejected(self):
        for rec in self:
            if rec.state in ('waiting_approval'):
                employee_id = self.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)])
                if not employee_id:
                    raise UserError(u'No existe un empleado asociado el usuario que creo el anticipo, por lo tanto el sistema de aprobaciones de anticipos no funciona. Consulte al administrador del sistema.')
                expense_manager_ids = employee_id.expense_manager_ids
                if not expense_manager_ids:
                    raise UserError(u'El empleado asociado al usuario que creo el anticipo no tiene definido un aprobador de tipo director. Consulte al administrador del sistema.')
                if self.env.uid not in expense_manager_ids.ids:
                    raise UserError(u'El usuario %s no tiene permitido rechazar este anticipo' % (self.env.user.name))
                else:
                    rec.state = 'rejected'
            elif rec.state in ('waiting_approval2'):
                employee_id = self.env['hr.employee'].search([('user_id', '=', rec.create_uid.id)])
                if not employee_id:
                    raise UserError(u'No existe un empleado asociado el usuario que creo el anticipo, por lo tanto el sistema de aprobaciones de anticipos no funciona. Consulte al administrador del sistema.')
                expense_treasury_id = employee_id.expense_treasury_id
                if not expense_treasury_id:
                    raise UserError(u'El empleado asociado al usuario que creo el anticipo no tiene definido un aprobador de tipo tesorería. Consulte al administrador del sistema.')
                if self.env.uid != expense_treasury_id.id:
                    raise UserError(u'El usuario %s no tiene permitido rechazar este anticipo' % (self.env.user.name))
                else:
                    rec.state = 'rejected2'            
            else:
                raise UserError(u'No es posible cancelar un anticipo en estado %s' % (rec.state))


    def action_draft(self):
        for rec in self:
            if rec.state in ('cancel','rejected','rejected2'):
                rec.state = 'draft'
            else:
                raise UserError(u'No es posible cancelar un anticipo en estado %s' % (rec.state))


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    advance_payment_ids = fields.One2many('account.advance.payment', 'purchase_order_id', string='Anticipos')


    @api.onchange('advance_payment_ids')
    def _onchange_advance_payment_ids(self):
        for order in self:
            if not order.partner_id and order.id:
                raise UserError(_("Debe seleccionar un cliente en la orden de venta antes de poder realizar un anticipo"))


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4
