from odoo import api, fields, models, exceptions, _
from datetime import date

STATE = [('draft', 'Draft'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('finalized', 'Finalized')]


class HrPayrollDebtCapacity(models.Model):
    _name = 'hr.payroll.debt.capacity'
    _description = 'Debt capacity for discounts'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    def _default_employee(self):
        user = self.env.user
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)])
        if employee:
            return employee
        else:
            return None

    name = fields.Char(default='New', readonly=True, required=True, copy=False)
    state = fields.Selection(string='State', selection=STATE, default='draft')
    date = fields.Date('Date', default=date.today())

    currency_id = fields.Many2one('res.currency', 'Currency',
                                  default=lambda self: self.env.user.company_id.currency_id.id,
                                  required=True)

    employee_id = fields.Many2one('hr.employee', 'Employee')
    identification_id = fields.Char('Identification')
    code = fields.Char('Code')
    requested_amount = fields.Float('Requested Amount')
    date_entry = fields.Date('Date of Entry')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    job_id = fields.Many2one('hr.job', 'Job', related='employee_id.job_id')

    """Type Contract"""
    contract_type_id = fields.Many2one('hr.contract.type', 'Type Contract')
    fixed = fields.Float('Fixed')
    expiration = fields.Date('Expiration')

    """Accruals"""
    wage = fields.Float('Wage')
    commissions = fields.Float('Commissions')
    overtime = fields.Float('Overtime')
    include_commission = fields.Boolean('Includes Commissions')
    includes_overtime = fields.Boolean('Includes Overtime')
    total_accruals = fields.Float('Total Accruals')
    net = fields.Float('Net')

    """Deductions"""
    health = fields.Float('Health')
    pension = fields.Float('Pension')
    pens_solidarity_fund = fields.Float('Pens Solidarity Fund')
    retention_at_source = fields.Float('Retention at Source')

    """Loans"""
    loans_line_ids = fields.One2many('hr.payroll.loans.line', 'debt_capacity_id')
    less_deductions = fields.Float('Less Deductions')

    percentage = fields.Float('Percentage Accrued')
    accrued = fields.Float('Accrued')
    deductions = fields.Float('Deductions')
    available_salary = fields.Float('Available Salary')
    approved = fields.Selection(selection=[('yes', 'Yes'), ('no', 'No')], string='Approved')

    documents_requested = fields.Char('Documents Requested')
    observations = fields.Text('Observations')

    """Elaborated"""
    elaborated_employee_id = fields.Many2one('hr.employee', 'Name', default=_default_employee)
    elaborated_job_id = fields.Many2one('hr.job', 'Job', related='elaborated_employee_id.job_id')
    date_received = fields.Date('Date Received', default=date.today())

    """I approve"""
    approve_employee_id = fields.Many2one('hr.employee', 'Name')
    approve_job_id = fields.Many2one('hr.job', 'Job', related='approve_employee_id.job_id')
    delivery_date = fields.Date('Delivery Date')

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'debt.capacity') or 'New'
        result = super(HrPayrollDebtCapacity, self).create(vals)
        return result

    @api.onchange('identification_id')
    def onchange_method(self):
        if self.identification_id:
            employee = self.env['hr.employee'].search([('identification_id', '=', self.identification_id)], limit=1)
            if employee:
                self.employee_id = employee.id

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.health = 0
        self.pension = 0
        self.pens_solidarity_fund = 0
        self.retention_at_source = 0
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')])
            if contract:
                self.date_entry = contract.date_start
                self.contract_type_id = contract.contract_type_id
                self.expiration = contract.date_end
                self.wage = contract.wage

    @api.onchange('employee_id')
    def calculate_loans(self):
        if self.employee_id:
            loans = self.env['hr.payroll.dis.aid'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'approved')])
            self.loans_line_ids.unlink()

            if loans:
                less_deductions = 0

                for loan in loans:
                    self.env['hr.payroll.loans.line'].create({
                        'dis_aid_id': loan.id,
                        'concept_id': loan.concept_id.id,
                        'monthly_fee': loan.monthly_fee,
                        'quote_to_pay': loan.quote_to_pay,
                        'debt_capacity_id': self.id,
                    })
                    less_deductions += loan.monthly_fee
                self.less_deductions = less_deductions
                self.deductions = less_deductions

    @api.onchange('employee_id', 'date')
    def calculate_discounts(self):
        if self.employee_id:
            payroll = self.env['hr.payslip'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'in', ('done', 'paid')),
                 ('date_to', '<=', self.date)], order="date_to desc, id desc",
                limit=1)
            print(payroll.name)
            if payroll:
                healths = self.env['hr.payroll.discount.variable'].search([('name', '=', 'SALUD')])
                pensions = self.env['hr.payroll.discount.variable'].search([('name', '=', 'PENSIÓN')])
                solidarity_founds = self.env['hr.payroll.discount.variable'].search(
                    [('name', '=', 'FONDO DE SOLIDARIDAD')])
                retention_sources = self.env['hr.payroll.discount.variable'].search(
                    [('name', '=', 'RETENCION EN LA FUENTE')])

                total_health = 0
                total_pension = 0
                total_solidarity = 0
                total_retention = 0

                for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in healths.salary_rule_id):
                    total_health += line.amount

                for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in pensions.salary_rule_id):
                    total_pension += line.amount

                for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in solidarity_founds.salary_rule_id):
                    total_solidarity += line.amount

                for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in retention_sources.salary_rule_id):
                    total_retention += line.amount

                self.health = abs(total_health)
                self.pension = abs(total_pension)
                self.pens_solidarity_fund = abs(total_solidarity)
                self.retention_at_source = abs(total_retention)

    @api.onchange('includes_overtime', 'include_commission')
    def calculate_overtime_commissions(self):
        if self.employee_id:

            payrolls = self.env['hr.payslip'].search(
                [('employee_id', '=', self.employee_id.id), ('state', 'in', ('done', 'paid')),
                 ('date_to', '<=', self.date)], order="date_from desc",
                limit=3)

            if payrolls:
                if self.includes_overtime:
                    overtimes = self.env['hr.payroll.discount.variable'].search([('name', '=', 'HORAS EXTRAS')])
                    total_overtime = 0

                    for payroll in payrolls:
                        for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in overtimes.salary_rule_id):
                            total_overtime += line.amount

                    self.overtime = total_overtime / 3

                if self.include_commission:
                    commissions = self.env['hr.payroll.discount.variable'].search([('name', '=', 'COMISIONES')])
                    total_commissions = 0

                    for payroll in payrolls:
                        for line in payroll.line_ids.filtered(lambda x: x.salary_rule_id in commissions.salary_rule_id):
                            total_commissions += line.amount

                    self.commissions = total_commissions / 3

    @api.onchange('health', 'pension', 'pens_solidarity_fund', 'retention_at_source', 'total_accruals')
    def calculate_total_net(self):
        total_net = self.total_accruals - (
                self.health + self.pension + self.pens_solidarity_fund + self.retention_at_source)
        self.net = total_net

    @api.onchange('overtime', 'wage', 'commissions')
    def calculate_total_accruals(self):
        self.total_accruals = (self.overtime + self.wage + self.commissions)

    @api.onchange('percentage')
    def calculate_net(self):
        if self.percentage != 0:
            if self.net > 0 and (self.percentage > 0 and self.percentage <= 50):
                self.accrued = (self.net * self.percentage) / 100
                self.available_salary = self.accrued - self.deductions

            else:
                raise exceptions.ValidationError(_('The accumulated percentage cannot be more than 50 or less than 0'))

    def approve(self):
        self.state = 'approved'


class LoansDetail(models.Model):
    _name = 'hr.payroll.loans.line'
    _description = 'Detail Loans on Debt Capacity'

    dis_aid_id = fields.Many2one('hr.payroll.dis.aid', 'Description')
    concept_id = fields.Many2one('hr.payroll.dis.aid.concept', 'Concept')
    monthly_fee = fields.Float('Amount')
    quote_to_pay = fields.Integer('Quote to Pay')
    debt_capacity_id = fields.Many2one('hr.payroll.debt.capacity')


class VariationsDiscounts(models.Model):
    _name = 'hr.payroll.discount.variable'
    _description = 'Discount Variable for Module Debt Capacity'

    name = fields.Char('Variation')
    salary_rule_id = fields.Many2many('hr.salary.rule')
