# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, exceptions, _
from odoo.exceptions import UserError, ValidationError, Warning
import xlrd
import base64
import datetime
import math
import re
from dateutil.relativedelta import relativedelta

TYPE_CONCEPT = [('loan', 'Loan'), ('embargoe', 'Embargoe'), ('libranza', 'Libranza'), ('aid', 'Aid')]


class HrPayrollDiscountAidConcept(models.Model):
    """Hr Payroll Discount/Aid Concept"""

    _name = "hr.payroll.dis.aid.concept"
    _description = "Discount/Aid Concepts"

    company_id = fields.Many2one('res.company', 'Company')

    code = fields.Char(string="Code", size=5)
    name = fields.Char(string="Concept")
    sequence_id = fields.Many2one(comodel_name='ir.sequence', string='Sequence', required=True)
    type = fields.Selection(string='Type', selection=TYPE_CONCEPT, required=True)
    event_id = fields.Many2one(comodel_name='hr.pv.event', string='Event', required=True)
    has_partner = fields.Boolean('Has Partner')
    partner_id = fields.Many2one('res.partner')

    """Other Fields"""
    default_rate = fields.Float(string='Default Rate', default=0)


class HrPayrollDiscountAidType(models.Model):
    """Hr Payroll Discount/Aid Type"""

    _name = "hr.payroll.dis.aid.type"
    _description = "Discount/Aid Types"

    code = fields.Char(string="Code", size=5)
    name = fields.Char(string="Type")
    event_id = fields.Many2one(comodel_name='hr.pv.event', string='Event', required=True)

    frequency = fields.Selection(string='Frequency',
                                 selection=[('biweekly', 'Biweekly'), ('monthly', 'Monthly'), ('biannual', 'Biannual'),
                                            ('annual', 'Annual')],
                                 default='monthly')

    is_extra_time = fields.Boolean(string="Apply as Overtime")

    min_percent = fields.Float(string="Minimum Percent")
    max_percent = fields.Float(string="Maximum Percent")
    allow_out_of_range = fields.Boolean(string="Allow out of Range", default=False)

    @api.onchange('min_percent', 'max_percent')
    def onchange_min_max_percent(self):
        if self.min_percent != 0 and self.max_percent != 0:
            if self.min_percent >= self.max_percent:
                raise exceptions.ValidationError(_('The minimum percentage cannot be greater than or equal to the '
                                                   'maximum percentage'))


class HrPayrollDiscountAidCommitted(models.Model):
    """Hr Payroll Discount/Aid Committed"""

    _name = "hr.payroll.dis.aid.committed"
    _description = "Committed to obtain founds to pay a Discount/Aid"

    dis_aid_id = fields.Many2one(
        comodel_name='hr.payroll.dis.aid',
        string='Discount/Aid',
        required=True)
    name = fields.Char(related="type_id.name")

    type_id = fields.Many2one(
        comodel_name='hr.payroll.dis.aid.type',
        string='Type',
        required=True)
    select_fix = fields.Selection(selection=[('compute', 'Compute'), ('value', 'Value'), ('percent', 'Percent'),
                                             ('val_ipc', 'Value with IPC increment'),
                                             ('val_percent', 'Value with percent increment')],
                                  string='Assigned By')

    start_date = fields.Date(string='Start Date', default=lambda self: fields.datetime.now(), required=True,
                             tracking=True)
    end_date = fields.Date(string='End Date', required=False)
    change_date = fields.Date(string='Change Date', default=lambda self: fields.datetime.now(), required=True,
                              tracking=True)
    fix_value = fields.Float(string="Value")
    fix_percent = fields.Float(string="Percent")

    @api.onchange('fix_percent')
    def onchange_fix_percent(self):
        if self.type_id:
            if self.fix_percent:
                if self.type_id.allow_out_of_range:
                    pass
                else:
                    if (self.fix_percent >= self.type_id.min_percent) and (
                            self.fix_percent <= self.type_id.max_percent):
                        pass
                    else:
                        raise exceptions.ValidationError(_('The fixed percentage is outside the ranges of the type'))

    @api.onchange('select_fix')
    def onchange_select_fix(self):
        self.fix_value = 0
        self.fix_percent = 0

    @api.onchange('start_date', 'end_date')
    def validate_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(_('The start date cannot be greater than the end date'))


class HrPayrollDiscountAid(models.Model):
    """Hr Payroll Discounts/Aid like Liens, Loans, etc."""

    _name = "hr.payroll.dis.aid"
    _description = "Discount/Aids like liens, loans, etc. given to employee"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company,
                                 index=1)
    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  required=True)

    name = fields.Char(string="Name")

    state = fields.Selection(string='State',
                             selection=[('draft', 'Draft'),
                                        ('approved', 'Approved'), ('finalized', 'Finalized'), ('canceled', 'Canceled')],
                             required=False, default='draft', copy=False)

    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True)
    salary_employee = fields.Float()
    concept_id = fields.Many2one(comodel_name='hr.payroll.dis.aid.concept', string='Concept', required=True)
    committed_ids = fields.One2many(comodel_name='hr.payroll.dis.aid.committed', inverse_name='dis_aid_id',
                                    string='Committed',
                                    required=True)
    debt_capacity_id = fields.Many2one('hr.payroll.debt.capacity', 'Debt Capacity')
    total_debt_capacity = fields.Float('Total Debt Capacity', related='debt_capacity_id.available_salary')

    total_pay = fields.Float('Total Pay')

    """New Fields"""
    credit_number = fields.Char('Credit Number', tracking=True)
    payment_type = fields.Selection(string='Assignment Type',
                                    selection=[('1', 'Monthly'),
                                               ('2', 'Bi-weekly')], tracking=True)
    half_value = fields.Float('Half Value', compute="_onchange_payment_type", tracking=True)

    fixed_quota_amount = fields.Float('Fixed Quota Amount', tracking=True)
    simulation_file = fields.Binary('Simulation File', tracking=True)
    simulation_file_name = fields.Char("File Name")

    identification_id = fields.Char(string='Identification No', readonly=True, tracking=True,
                                    related="employee_id.identification_id", states={'draft': [('readonly', False)]})

    """Boolean Fields"""
    control_balance = fields.Boolean('Control Balance', tracking=True, default=False)
    has_fixed_quota = fields.Boolean(string='Manage Fixed Quota', default=False, tracking=True)
    has_partner = fields.Boolean(string="Manage Partner", default=False, tracking=True,
                                 related='concept_id.has_partner')
    has_manual_terms = fields.Boolean(string="Manual Terms", default=False, tracking=True)

    concept_type = fields.Char(compute="get_concept_type", tracking=True)

    """Conditional fields"""
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner', related='concept_id.partner_id')

    """Discount General Information"""
    total = fields.Float(string="Total Value", required=False)
    annual_effective_rate = fields.Float(string='Annual Effective Rate', required=True, default=0,
                                         tracking=True)
    annual_nominal_rate = fields.Float(string='Annual Nominal Rate', required=False, tracking=True)
    monthly_effective_rate = fields.Float(string='Monthly Effective Rate', required=False, tracking=True)
    monthly_nominal_rate = fields.Float(string='Monthly Nominal Rate', required=False, tracking=True)
    terms_in_years = fields.Float(string="Terms in Years", required=False, tracking=True)
    terms_in_months = fields.Integer(string="Terms in months", required=False, tracking=True)
    date = fields.Date(string='Date', default=lambda self: fields.datetime.now(), required=True,
                       tracking=True)
    first_payment_date = fields.Date(string='First Payment Date', default=lambda self: fields.datetime.now(),
                                     required=True,
                                     tracking=True)
    end_date = fields.Date(string='End Date', tracking=True)
    # real_end_date = fields.Date(string='Real End Date', tracking=True)

    """Discount Summary Information"""
    monthly_fee = fields.Float(string="Monthly fee", required=True, tracking=True, copy=False, default=0)
    total_amount = fields.Float(string="Total Amount", required=True, tracking=True, copy=False,
                                default=0)
    capital_to_pay = fields.Float(string="Capital to Pay", compute="get_capital_to_pay", copy=False)

    total_to_pay = fields.Float(string="Total to Pay", required=False, tracking=True, copy=False)
    total_paid = fields.Float(string="Total Paid", tracking=True, copy=False)
    total_payable = fields.Float(string="Total Payable", compute="compute_totals", tracking=True,
                                 copy=False)

    quote_to_pay = fields.Integer('Quote to Pay', compute="compute_totals", tracking=True, copy=False)
    quote_payed = fields.Integer('Quote Payed', compute="compute_totals", tracking=True, copy=False)
    total_quote = fields.Integer('Total Quotes', compute="compute_totals", tracking=True, copy=False)

    total_original = fields.Float(string="Total Original", tracking=True, copy=False)
    observation = fields.Text('Observations', tracking=True, copy=False)

    line_ids = fields.One2many(comodel_name='hr.payroll.dis.aid.line', inverse_name='dis_aid_id', string='Line_ids',
                               required=False, copy=False)
    payment_line_ids = fields.One2many(comodel_name='hr.payroll.dis.aid.payment.line', inverse_name='dis_aid_id',
                                       string='Payment Lines',
                                       required=False, copy=False)

    """Embargoes General Information"""
    embargo = fields.Char('Embargo', tracking=True)
    process_number = fields.Char('Process Number', tracking=True)
    court_account_number = fields.Char('Court Account Number', tracking=True)
    file_number = fields.Char('File Number', tracking=True)
    date_foreclosure = fields.Date('Date of Foreclosure', tracking=True)
    embargo_type = fields.Selection(
        string='Embargo Type',
        selection=[('food', 'Food'),
                   ('cooperatives', 'Cooperatives'),
                   ('judicial', 'Judicial Deposit'), ('civil', 'Civil')],
        required=False, tracking=True)
    priority = fields.Integer('Priority', tracking=True)
    initial_balance = fields.Float('Initial Balance', tracking=True)
    current_balance = fields.Float('Current Balance', tracking=True)

    """Payroll Verification"""
    respect_smlv = fields.Boolean('Respect SMLV', tracking=True)
    respect_legal_discount = fields.Boolean('Respects Legal Discounts', tracking=True)

    """Courts Fields"""
    court_id = fields.Many2one('hr.court', string='Court', tracking=True)
    court_code = fields.Char('Code', related='court_id.code', tracking=True)
    court_nit = fields.Char('NIT', related='court_id.nit', tracking=True)
    court_phone = fields.Char('Phone', related='court_id.phone', tracking=True)
    court_city = fields.Many2one('res.city', string='City', related='court_id.city', tracking=True)
    court_address = fields.Char('Address', related='court_id.address', tracking=True)

    """Boolean fields"""
    check_change_terms = fields.Selection(selection=[('year', 'year'), ('month', 'month'), ('none', 'none')],
                                          default='none')
    manual_simulation = fields.Boolean('Manual Simulation', tracking=True)

    """Plaintiff Fields"""
    type_identification_applicant = fields.Char('Identification Type', tracking=True)
    number_claimant_identification = fields.Char('No. Identification Claimant', tracking=True)
    company_name_names = fields.Char('Company Name / Names', tracking=True)
    surname = fields.Char('Surname', tracking=True)

    """Override Methods"""

    @api.model
    def create(self, values):
        # Add code here
        sequence = self.env['hr.payroll.dis.aid.concept'].search([('id', '=', values['concept_id'])]).sequence_id

        if sequence.use_date_range:
            values['name'] = sequence.next_by_id(sequence_date=values['date'])
        else:
            values['name'] = sequence.next_by_id()

        return super(HrPayrollDiscountAid, self).create(values)

    """General Methods"""

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            if self.concept_id.company_id:
                self.concept_id = False
            self.employee_id = False
            self.identification_id = False

    @api.onchange('concept_id', 'has_fixed_quota')
    def onchange_has_fixed_quota(self):
        if self.has_fixed_quota:
            self.annual_effective_rate = 0
        else:
            self.annual_effective_rate = self.concept_id.default_rate
            self.has_manual_terms = True

    @api.onchange('control_balance')
    def onchange_control_balance(self):
        if not self.control_balance:
            self.has_fixed_quota = True
            self.annual_effective_rate = 0

    @api.onchange('concept_id')
    def get_concept_type(self):
        if self.concept_id:
            self.concept_type = self.concept_id.type
        else:
            self.concept_type = None

    @api.onchange('employee_id')
    def employee_salary(self):
        if self.employee_id:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            self.salary_employee = contract.wage
            self.company_id = self.employee_id.company_id

    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if self.payment_type == 'both':
            if self.has_fixed_quota:
                self.half_value = self.fixed_quota_amount / 2
            else:
                self.half_value = self.monthly_fee / 2
        else:
            self.half_value = 0

    @api.onchange('annual_effective_rate')
    def calculate_rates(self):
        self.monthly_effective_rate = round((self.annual_effective_rate / 12), 2)
        if self.payment_type:
            self.monthly_effective_rate = (self.annual_effective_rate / (12 * int(self.payment_type)))

            monthly_rate = (((1 + (self.annual_effective_rate / 100)) ** (1 / 12 * int(self.payment_type))) - 1)
            self.annual_nominal_rate = monthly_rate * (12 * int(self.payment_type))
            self.monthly_nominal_rate = monthly_rate

    @api.depends('terms_in_months')
    @api.onchange('terms_in_years')
    def calculate_months(self):
        if self.check_change_terms in ('none', 'month'):
            if self.check_change_terms == 'none':
                self.check_change_terms = 'year'

                self.terms_in_months = int(math.ceil(self.terms_in_years * 12))

            if self.check_change_terms == 'month':
                self.check_change_terms = 'none'

    @api.depends('terms_in_years')
    @api.onchange('terms_in_months')
    def calculate_years(self):
        if self.check_change_terms in ('none', 'year'):
            if self.check_change_terms == 'none':
                self.check_change_terms = 'month'

                self.terms_in_years = round((self.terms_in_months / 12), 2)

            if self.check_change_terms == 'year':
                self.check_change_terms = 'none'

    @api.depends('date', 'terms_in_months')
    @api.onchange('date', 'terms_in_months')
    def get_end_date(self):
        for dis_aid in self:
            if dis_aid.control_balance:
                dis_aid.end_date = self.date + relativedelta(months=dis_aid.terms_in_months - 1)
            else:
                dis_aid.end_date = False

    @api.onchange('fixed_quota_amount', 'total', 'payment_type')
    def get_terms_in_months(self):
        if not self.control_balance and self.fixed_quota_amount and self.total and self.fixed_quota_amount > 0 and self.total > 0:
            if not self.has_manual_terms:
                self.check_change_terms = 'none'
                self.terms_in_months = int(math.ceil(self.total / (self.fixed_quota_amount * int(self.payment_type))))
            else:
                self.terms_in_months = 0

    @api.onchange('fixed_quota_amount', 'terms_in_months', 'payment_type')
    def get_total(self):
        if self.control_balance and self.fixed_quota_amount and self.terms_in_months and self.fixed_quota_amount > 0 and self.terms_in_months > 0:
            self.total = round((self.fixed_quota_amount * self.terms_in_months * int(self.payment_type)), 2)

    def get_capital_to_pay(self):
        for dis in self:

            total_payed = 0
            interest_payed = 0

            for dis_payment in dis.payment_line_ids:
                total_payed += dis_payment.payment_value

            for dis_line in dis.line_ids:
                if dis_line.state == 'payed':
                    interest_payed += dis_line.interest_pay

            dis.capital_to_pay = dis.total_amount - total_payed + interest_payed

    def compute_totals(self):
        for dis_aid in self:
            total_quote = dis_aid.terms_in_months * int(dis_aid.payment_type)
            quote_payed = 0
            total_payable = 0

            for line in dis_aid.line_ids:
                if line.state in ('created', 'approved'):
                    total_payable += line.monthly_pay

                if line.state in ('payed'):
                    quote_payed += 1 if line.code > 0 else quote_payed

            total_to_pay = 0
            quote_to_pay = 0
            for dis_aid_line in dis_aid.line_ids:
                if dis_aid_line.state == 'approved' and dis_aid_line.monthly_pay != 0:
                    total_to_pay += dis_aid_line.monthly_pay
                    quote_to_pay += 1

            if dis_aid.control_balance:
                dis_aid.total_payable = dis_aid.total_to_pay - dis_aid.total_paid
                dis_aid.quote_payed = quote_payed
                dis_aid.quote_to_pay = quote_to_pay
                dis_aid.total_quote = total_quote
            else:
                dis_aid.total_payable = 0

                dis_aid.quote_payed = quote_payed
                dis_aid.quote_to_pay = 0
                dis_aid.total_quote = 0

    @api.constrains('employee_id', 'identification_id')
    def _check_employee(self):
        for item in self:
            if item.employee_id and item.employee_id.identification_id:
                if item.identification_id != item.employee_id.identification_id:
                    raise UserError(
                        _("El número de identificación no corresponde al empleado")
                    )
            elif item.identification_id and not item.employee_id:
                dis_aid_id = self.search([
                    ('id', '=', self.id)])
                if dis_aid_id and dis_aid_id.employee_id and item.identification_id != dis_aid_id.employee_id.identification_id:
                    raise UserError(
                        _("El número de identificación no corresponde al empleado")
                    )

    @api.onchange('identification_id')
    def onchange_identification_id(self):
        if self.identification_id:
            employee = self.env['hr.employee'].search(
                [('identification_id', '=', self.identification_id), ('company_id', '=', self.company_id.id)])
            if employee:
                self.employee_id = employee.id

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            if contract:
                self.employee_id_current_salary = contract.wage

    def _validate_credit_number(self):
        if self.credit_number:
            if not re.match('^[0-9]+$', self.credit_number):
                raise exceptions.ValidationError(_('Not a valid Credit Number, is not a number'))

    @api.constrains('credit_number')
    def _check_valid_credit_number(self):
        self._validate_credit_number()

    @api.onchange('embargo_type')
    def _onchange_embargo_type(self):
        if self.embargo_type:
            if self.embargo_type == 'food':
                self.priority = 1

            if self.embargo_type == 'cooperatives':
                self.priority = 2

            if self.embargo_type == 'judicial':
                self.priority = 3

            if self.embargo_type == 'civil':
                self.priority = 4

            dis_aids = self.env['hr.payroll.dis.aid'].search(
                [('priority', '!=', 0), ('employee_id', '=', self.employee_id.id), ('state', '=', 'approved')],
                order='priority asc', limit=1)

            res = {}
            if dis_aids:
                if dis_aids.priority <= self.priority:
                    embargoe_name = dis_aids.name
                    res = {
                        'title': _('Warning'),
                        'message': _(
                            'The employee has another embargoe with lowest or equal priority. The embargo is ' + embargoe_name)
                    }
            if res:
                return {'warning': res}

        else:
            self.priority = 0

    def create_dis_aid_line(self, dis_aid_id=False, committed_id=False, select_fix=False, code=False, name=False,
                            date=False,
                            end_date=False, capital_pay=False, interest_pay=False,
                            monthly_pay=False, balance=False):

        if self.control_balance:
            if select_fix == 'compute':
                new_end_date = date
            else:
                new_end_date = end_date
        else:
            new_end_date = end_date

        return self.env['hr.payroll.dis.aid.line'].create(
            {
                'dis_aid_id': dis_aid_id,
                'committed_id': committed_id,
                'code': code,
                'name': name,
                'date': date,
                'end_date': new_end_date,
                'capital_pay': capital_pay,
                'interest_pay': interest_pay,
                'monthly_pay': monthly_pay,
                'balance': balance,
            }
        )

    def create_dis_aid_payment_line(self, dis_aid_id, dis_aid_line_id, name, date, payment_value, payslip_line_id):
        last_code = self.env['hr.payroll.dis.aid.payment.line'].search(
            [('dis_aid_id', '=', dis_aid_id)], order='code desc', limit=1).code

        payment_line = self.env['hr.payroll.dis.aid.payment.line'].create(
            {
                'dis_aid_id': dis_aid_id,
                'dis_aid_line_id': dis_aid_line_id,
                'code': last_code + 1,
                'name': name,
                'date': date,
                'payment_value': payment_value,
                'payslip_line_id': payslip_line_id,
            }
        )

        self.calculate_total_pay()

        if not payment_line.dis_aid_line_id or (
                payment_line.dis_aid_line_id and payment_line.dis_aid_line_id.committed_id.select_fix != 'compute'):
            self.recalc_quotes_with_new_balance()

        payment_line.balance = self.total_to_pay

        return payment_line

    def calculate_total_pay(self):
        if self.payment_line_ids:
            total_payed = 0
            interest_payed = 0

            for dis_payment in self.payment_line_ids:
                total_payed += dis_payment.payment_value

            for dis_line in self.line_ids:
                if dis_line.state == 'payed':
                    interest_payed += dis_line.interest_pay

            self.capital_to_pay = self.total_amount - total_payed + interest_payed
            self.total_paid = total_payed
            if (self.total_paid >= self.total_to_pay) and self.control_balance:
                self.action_finish()
            else:
                if self.state == 'finished':
                    self.state == 'processed'
        else:
            self.total_paid = 0

        if self.total_to_pay > 0:
            self.total_payable = self.total_to_pay - self.total_paid
        else:
            self.total_payable = 0

    def recalc_quotes_with_new_balance(self, quotes=0):
        if quotes != 0:
            term_in_months = quotes
        else:
            term_in_months = self.quote_to_pay

        if self.control_balance:
            for line in self.line_ids:
                if line.state == 'approved':
                    line.pv_id.update({
                        'state': 'cancel',
                    })

                    line.state = 'cancel'

        if not self.control_balance:

            """
            valid_committed = self.committed_ids.filtered(lambda x: x.select_fix == 'compute')
            if not valid_committed:
                raise exceptions.ValidationError(_('Commitments do not have a calculated type'))
            """

            code = 0
            for committed in self.committed_ids:
                dis_aid_line = self.env['hr.payroll.dis.aid.line'].search(
                    [('dis_aid_id.id', '=', self.id), ('committed_id', '=', committed.id),
                     ('state', '!=', 'cancel')])

                if not dis_aid_line:
                    line = self.create_dis_aid_line(
                        dis_aid_id=self.id,
                        committed_id=committed.id,
                        select_fix=committed.select_fix,
                        code=code + 1,
                        name=_('Fixed Quote'),
                        date=committed.start_date,
                        end_date=committed.end_date,
                        capital_pay=0,
                        interest_pay=0,
                        monthly_pay=self.fixed_quota_amount if committed.select_fix == 'compute' else 0,
                        balance=0,
                    )

                    code += 1

                    line.create_pv()





        elif (
                not self.has_fixed_quota and self.total and self.total > 0 and self.terms_in_years and self.terms_in_years > 0) or \
                (self.has_fixed_quota and ((self.fixed_quota_amount and self.fixed_quota_amount > 0)) or (
                        self.total and self.total > 0)):

            """
            if not self.has_fixed_quota:
                monthly_rate = (((1 + (self.annual_effective_rate / 100)) ** (1 / 12)) - 1)
                if monthly_rate > 0:
                    self.monthly_fee = round(
                        (total_to_pay * (monthly_rate * ((1 + monthly_rate) ** term_in_months))) / (
                                ((1 + monthly_rate) ** term_in_months) - 1), 2)
                else:
                    self.monthly_fee = round(total_to_pay / term_in_months, 2)
            else:
                monthly_rate = 0
                # self.monthly_fee = round(total_to_pay / term_in_months, 2)
                self.monthly_fee = self.fixed_quota_amount
            """

            valid_committed = self.committed_ids.filtered(lambda x: x.select_fix == 'compute')
            # if not valid_committed:
            #   raise exceptions.ValidationError(_('Commitments do not have a calculated type'))

            if len(valid_committed) > 1:
                raise exceptions.UserError(_('Commitments can not have two of calculated type.'))

            line = False

            monthly_rate = self.monthly_nominal_rate
            balance_payable = self.capital_to_pay
            quote = self.quote_payed + 1
            if valid_committed:

                if self.monthly_fee == 0:
                    raise exceptions.ValidationError(_('Term in months has not been assigned'))

                while balance_payable > 0:
                    if balance_payable + round((balance_payable * monthly_rate), 2) > self.monthly_fee:
                        interest_pay = round((balance_payable * monthly_rate), 2)
                        capital_pay = self.monthly_fee - interest_pay
                        balance_payable -= capital_pay

                        if balance_payable < 100:
                            capital_pay += balance_payable
                            balance_payable = 0

                    else:
                        interest_pay = round((balance_payable * monthly_rate), 2)
                        capital_pay = balance_payable
                        balance_payable = 0

                    monthly_pay = capital_pay + interest_pay

                    if self.payment_type == '1':
                        date = self.first_payment_date + relativedelta(months=quote - 1)
                    else:
                        if self.first_payment_date.day <= 15:
                            day = 1
                        else:
                            day = 16
                        initial_date = datetime.date(self.first_payment_date.year, self.first_payment_date.month, day)

                        if quote >= 3:
                            estimate_date = initial_date + relativedelta(days=(15 * (quote - 2)) + 16)
                        else:
                            estimate_date = initial_date + relativedelta(days=16 * (quote - 1))

                        if estimate_date.day <= 15:
                            day = 1
                        else:
                            day = 16
                        date = datetime.date(estimate_date.year, estimate_date.month, day)

                    line = self.create_dis_aid_line(
                        dis_aid_id=self.id,
                        committed_id=valid_committed.id,
                        select_fix=valid_committed.select_fix,
                        code=quote,
                        name=_('Quote No. ') + str(quote),
                        date=date,
                        capital_pay=capital_pay,
                        interest_pay=interest_pay,
                        monthly_pay=monthly_pay,
                        balance=balance_payable,

                    )

                    line.create_pv()

                    quote += 1

            # Update end_date fields when register a pay.
            if line:
                self.end_date = line.date

            for committed in self.committed_ids.filtered(lambda x: x.select_fix != 'compute'):
                dis_aid_line = self.env['hr.payroll.dis.aid.line'].search(
                    [('dis_aid_id.id', '=', self.id), ('committed_id', '=', committed.id), ('state', '!=', 'cancel')])

                if not dis_aid_line:
                    line = self.create_dis_aid_line(
                        dis_aid_id=self.id,
                        committed_id=committed.id,
                        select_fix=committed.select_fix,
                        code=quote,
                        name=_('Fixed Quote'),
                        date=committed.start_date,
                        end_date=committed.end_date,
                        capital_pay=0,
                        interest_pay=0,
                        monthly_pay=0,
                        balance=0,
                    )

                    line.create_pv()

                    quote += 1

            total_to_pay = 0
            quote_to_pay = 0
            for dis_line in self.line_ids:
                if dis_line.state == 'approved' and dis_line.monthly_pay != 0:
                    total_to_pay += dis_line.monthly_pay
                    quote_to_pay += 1

            if self.control_balance:
                if self.has_fixed_quota:
                    total_to_pay = self.total - self.total_paid

                self.total_to_pay = self.total_paid + total_to_pay
                self.quote_to_pay = quote_to_pay

        self.calculate_total_pay()

    """Buttons Methods"""

    def action_simulate(self):
        for dis in self:
            if not dis.committed_ids:
                raise exceptions.ValidationError(_('Must have at least one committed'))

            if not dis.control_balance:

                """
                valid_committed = self.committed_ids.filtered(lambda x: x.select_fix == 'compute')
                if not valid_committed:
                    raise exceptions.ValidationError(_('Commitments do not have a calculated type'))
                """

                dis.line_ids.unlink()

                code = 0
                for committed in dis.committed_ids:
                    line = dis.create_dis_aid_line(
                        dis_aid_id=dis.id,
                        committed_id=committed.id,
                        select_fix=committed.select_fix,
                        code=code + 1,
                        name=_('Fixed Quote'),
                        date=dis.first_payment_date if committed.select_fix == 'compute' else committed.start_date,
                        end_date=dis.first_payment_date if committed.select_fix == 'compute' else committed.end_date,
                        capital_pay=0,
                        interest_pay=0,
                        monthly_pay=dis.fixed_quota_amount if committed.select_fix == 'compute' else 0,
                        balance=0,
                    )
                    code += 1

            elif (
                    not dis.has_fixed_quota and dis.total and dis.total > 0 and dis.terms_in_years and dis.terms_in_years > 0) or \
                    (dis.has_fixed_quota and ((dis.fixed_quota_amount and dis.fixed_quota_amount > 0)) or (
                            dis.total and dis.total > 0)):

                if not dis.has_fixed_quota:
                    total_balance = dis.total
                    dis.total_amount = total_balance
                    monthly_rate = dis.monthly_nominal_rate
                    if monthly_rate > 0:
                        dis.monthly_fee = round(
                            (dis.total * (monthly_rate * (
                                    (1 + monthly_rate) ** (dis.terms_in_months * int(dis.payment_type))))) / (
                                    ((1 + monthly_rate) ** (dis.terms_in_months * int(dis.payment_type))) - 1), 2)
                    else:
                        dis.monthly_fee = round(total_balance / (dis.terms_in_months * int(dis.payment_type)), 2)
                else:
                    if dis.has_manual_terms:
                        total_balance = dis.fixed_quota_amount * (dis.terms_in_months * int(dis.payment_type))
                    else:
                        total_balance = dis.total

                    monthly_rate = 0
                    dis.monthly_fee = dis.fixed_quota_amount
                    dis.total_amount = total_balance

                valid_committed = dis.committed_ids.filtered(lambda x: x.select_fix == 'compute')
                # if not valid_committed:
                #   raise exceptions.ValidationError(_('Commitments do not have a calculated type'))

                dis.line_ids.unlink()

                line = dis.create_dis_aid_line(
                    dis_aid_id=dis.id,
                    committed_id=False,
                    select_fix=False,
                    code=0,
                    name=_('Quote No. 0'),
                    date=dis.date,
                    capital_pay=0,
                    interest_pay=0,
                    monthly_pay=0,
                    balance=total_balance,
                )

                if len(valid_committed) > 1:
                    raise exceptions.UserError(_('Commitments can not have two of calculated type.'))

                balance_payable = total_balance
                quote = 1
                if valid_committed:

                    if dis.monthly_fee == 0:
                        raise exceptions.ValidationError(
                            _('Term in months or the value of the quote has not been assigned'))

                    while balance_payable > 0:
                        if balance_payable + round((balance_payable * monthly_rate), 2) > dis.monthly_fee:
                            interest_pay = round((balance_payable * monthly_rate), 2)
                            capital_pay = dis.monthly_fee - interest_pay
                            balance_payable -= capital_pay

                            if balance_payable < 100:
                                capital_pay += balance_payable
                                balance_payable = 0

                        else:
                            interest_pay = round((balance_payable * monthly_rate), 2)
                            capital_pay = balance_payable
                            balance_payable = 0

                        monthly_pay = capital_pay + interest_pay

                        date = ''
                        if dis.payment_type == '1':
                            date = dis.first_payment_date + relativedelta(months=quote - 1)
                        else:
                            if dis.first_payment_date.day <= 15:
                                day = 1
                            else:
                                day = 16
                            initial_date = datetime.date(dis.first_payment_date.year, dis.first_payment_date.month, day)

                            if quote >= 3:
                                estimate_date = initial_date + relativedelta(days=(15 * (quote - 2)) + 16)
                            else:
                                estimate_date = initial_date + relativedelta(days=16 * (quote - 1))

                            if estimate_date.day <= 15:
                                day = 1
                            else:
                                day = 16
                            date = datetime.date(estimate_date.year, estimate_date.month, day)

                        line = dis.create_dis_aid_line(
                            dis_aid_id=dis.id,
                            committed_id=valid_committed.id,
                            select_fix=valid_committed.select_fix,
                            code=quote,
                            name=_('Quote No. ') + str(quote),
                            date=date,
                            capital_pay=capital_pay,
                            interest_pay=interest_pay,
                            monthly_pay=monthly_pay,
                            balance=balance_payable,
                        )

                        quote += 1

                    if dis.has_fixed_quota:
                        dis.total_to_pay = dis.total
                    else:
                        dis.total_to_pay = dis.monthly_fee * dis.terms_in_months * int(dis.payment_type)

                    for committed in dis.committed_ids.filtered(lambda x: x.select_fix != 'compute'):
                        line = dis.create_dis_aid_line(
                            dis_aid_id=dis.id,
                            committed_id=committed.id,
                            select_fix=committed.select_fix,
                            code=quote,
                            name=_('Fixed Quote'),
                            date=committed.start_date,
                            end_date=committed.end_date,
                            capital_pay=0,
                            interest_pay=0,
                            monthly_pay=0,
                            balance=0,
                        )
                    quote += 1
                else:
                    raise exceptions.UserError(_("Pending data to be filled"))

    def load_data(self):
        for rec in self:
            if rec.simulation_file:
                rec.line_ids.unlink()
                workbook = xlrd.open_workbook(
                    file_contents=base64.decodestring(
                        rec.simulation_file))
                row_list = []
                last_sheet = workbook.sheet_by_index(-1)
                for row in range(1, last_sheet.nrows):
                    row_list.append(last_sheet.row_values(row))
                for line_list in row_list:
                    rec_data = {
                        'code': 0,
                        'name': '',
                        'date': rec.date,
                        'capital_pay': 0,
                        'interest_pay': 0,
                        'monthly_pay': 0,
                        'balance': 0,
                    }
                    if line_list[0]:
                        rec_data.update({'code': line_list[0]})
                    if line_list[1]:
                        rec_data.update({'name': line_list[1]})
                    if line_list[2]:
                        rec_data.update({'date': line_list[2]})
                    if line_list[3]:
                        rec_data.update({'capital_pay': line_list[3]})
                    if line_list[4]:
                        rec_data.update({'interest_pay': line_list[4]})
                    if line_list[5]:
                        rec_data.update({'monthly_pay': line_list[5]})
                    if line_list[6]:
                        rec_data.update({'balance': line_list[6]})
                    if rec_data:
                        rec_data.update({'dis_aid_id': rec.id})
                        self.env['hr.payroll.dis.aid.line'].create(rec_data)

            else:
                raise exceptions.UserError(_('No file uploaded yet '))

    def action_approve(self):
        for dis in self:
            if dis.state == 'draft':
                dis.action_simulate()

                for line in dis.line_ids:
                    if line.code != 0:
                        line.create_pv()

                dis.state = 'approved'

    def action_finish(self):
        for dis in self:
            if dis.state == 'approved':
                if dis.line_ids:
                    for line in dis.line_ids:
                        if line.pv_id:
                            if line.state == 'payed':
                                line.pv_id.state = 'processed'

                            elif line.state == 'approved':
                                if self.env['hr.payroll.dis.aid.payment.line'].search(
                                        [('dis_aid_line_id', '=', line.id)]):
                                    line.pv_id.state = 'processed'
                                else:
                                    line.pv_id.state = 'cancel'
                                    line.state = 'cancel'
                            else:
                                line.pv_id.state = 'cancel'
                                line.state = 'cancel'

                dis.end_date = fields.datetime.now()
                dis.state = 'finalized'

    def action_cancel(self):
        for dis in self:
            if dis.state in ('draft', 'approved'):
                if dis.line_ids:
                    for line in dis.line_ids:
                        if line.pv_id:
                            if line.state == 'payed':
                                line.pv_id.state = 'processed'

                            elif line.state == 'approved':
                                if self.env['hr.payroll.dis.aid.payment.line'].search(
                                        [('dis_aid_line_id', '=', line.id)]):
                                    line.pv_id.state = 'processed'
                                    line.state = 'cancel'
                                else:
                                    line.pv_id.state = 'cancel'
                                    line.state = 'cancel'

                            else:
                                line.pv_id.state = 'cancel'

                dis.state = 'canceled'

    def action_dis_aid_simulate(self):
        """Massive Simulate Dis/AID."""
        flag = False

        dis_aid = ''
        more_info = ''

        for dis in self:
            if dis.state == 'draft':
                try:
                    dis.action_simulate()
                except:
                    flag = True

                    if not dis_aid:
                        dis_aid += str(dis.name)
                    else:
                        dis_aid += ', ' + str(dis.name)

                    if not more_info:
                        more_info += str(_(str(dis.name) + ': has a problem for simulate.'))
                    else:
                        more_info += '\n' + str(_(str(dis.name) + ': has a problem for simulate.'))

            else:
                flag = True
                if not dis_aid:
                    dis_aid += str(dis.name)
                else:
                    dis_aid += ', ' + str(dis.name)
        if flag:
            raise ValidationError(_(
                'Some Discounts/Aids are not in Draft state or have another issue.\n\n Records related: ' + dis_aid))

    def action_dis_aid_approve(self):
        """Massive Approve Dis/AID."""
        flag = False

        dis_aid = ''
        more_info = ''

        for dis in self:
            if dis.state == 'draft':
                try:
                    dis.action_approve()
                except:
                    flag = True

                    if not dis_aid:
                        dis_aid += str(dis.name)
                    else:
                        dis_aid += ', ' + str(dis.name)

                    if not more_info:
                        more_info += str(_(str(dis.name) + ': has a problem for approve.'))
                    else:
                        more_info += '\n' + str(_(str(dis.name) + ': has a problem for approve.'))

            else:
                flag = True
                if not dis_aid:
                    dis_aid += str(dis.name)
                else:
                    dis_aid += ', ' + str(dis.name)
        if flag:
            raise ValidationError(_(
                'Some Discounts/Aids are not in Draft state or have another issue.\n\n Records related:- ' + dis_aid))


class HrPayrollDiscountAidLine(models.Model):
    """Hr Payroll Discount/Aid Line"""

    _name = "hr.payroll.dis.aid.line"
    _description = "Amortization Table for HR Payroll Discount"
    _index = 'dis_aid_id, code'

    dis_aid_id = fields.Many2one(comodel_name='hr.payroll.dis.aid', string='Discount/Aid', required=True)
    pv_id = fields.Many2one(comodel_name='hr.pv', string='Related Payroll Variant', required=False)
    committed_id = fields.Many2one(comodel_name='hr.payroll.dis.aid.committed', string='Related Committed',
                                   required=False)
    state = fields.Selection(string='State',
                             selection=[('created', 'Created'),
                                        ('approved', 'Approved'),
                                        ('payed', 'Payed'),
                                        ('cancel', 'Cancel'), ],
                             required=True, default='created')
    code = fields.Integer(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Payment Date')
    end_date = fields.Date(string='End Date')
    capital_pay = fields.Float(string='Capital Payment', required=True)
    interest_pay = fields.Float(string='Interest Payment', required=True)
    monthly_pay = fields.Float(string='Monthly Payment', required=True)
    balance = fields.Float(string='Balance', required=True)

    def create_pv(self):
        self.ensure_one()

        line = self
        date = str(line.date) + ' ' + '05:00:00'
        pv_date = datetime.datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

        end_date = str(line.end_date) + ' ' + '05:00:00'
        pv_end_date = False
        if line.end_date:
            pv_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')

        event_id = line.committed_id.type_id.event_id if line.committed_id.select_fix not in (
            'compute') else line.dis_aid_id.concept_id.event_id

        if line.committed_id.select_fix == 'compute':
            pv_amount = line.monthly_pay
        elif line.committed_id.select_fix == 'percent':
            pv_amount = 0
        else:
            pv_amount = line.committed_id.fix_value

        new_pv = {
            'company_id': line.dis_aid_id.company_id.id,
            'type_id': event_id.type_id.id,
            'subtype_id': event_id.subtype_id.id,
            'event_id': event_id.id,
            'employee_id': line.dis_aid_id.employee_id.id,
            'identification_id': line.dis_aid_id.employee_id.identification_id,
            'percentage': line.committed_id.fix_percent if line.committed_id.select_fix == 'percent' else 0,
            'amount': pv_amount,
            'description': line.name,
            'start_date': pv_date,
            'end_date': pv_end_date,
            'is_dis_aid': True,
            'dis_aid_id': line.dis_aid_id.id,
            'capital_amount': line.capital_pay,
            'interest_amount': line.interest_pay,
        }

        pv = self.env['hr.pv'].sudo().create(new_pv)
        pv.write({
            'state': 'approved',
        })

        line.pv_id = pv.id

        line.state = 'approved'


class HrPayrollDiscountAidPaymentLine(models.Model):
    """Hr Payroll Discount/Aid Payment Line"""

    _name = "hr.payroll.dis.aid.payment.line"
    _description = "Payments for HR Payroll Discount"
    _index = 'dis_aid_id, code'

    dis_aid_id = fields.Many2one(comodel_name='hr.payroll.dis.aid', string='Discount/Aid', required=True)
    dis_aid_line_id = fields.Many2one(comodel_name='hr.payroll.dis.aid.line', string='Discount/Aid Line',
                                      required=False)
    code = fields.Integer(string='Code', required=True)
    name = fields.Char(string='Name', required=True)
    date = fields.Date(string='Payment Date')
    payment_value = fields.Float(string='Payment Value', required=True)
    payslip_line_id = fields.Many2one('hr.payslip.line', 'Payslip Line')
    balance = fields.Float('Balance')


class HrCourt(models.Model):
    _name = 'hr.court'
    _description = 'Court for embargoes in discounts/aids'

    code = fields.Char('Code', tracking=True)
    name = fields.Char('Name')
    nit = fields.Char('NIT', tracking=True)
    phone = fields.Char('Phone', tracking=True)
    city = fields.Many2one('res.city', string='City', tracking=True)
    address = fields.Char('Address', tracking=True)
