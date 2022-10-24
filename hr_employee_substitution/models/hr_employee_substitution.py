from odoo import api, fields, models, _
from datetime import date

STATE = [('draft', 'Draft'), ('processed', 'Processed'), ('completed', 'Completed'), ('cancel', 'Cancel')]

SELECTION_GROUP = [('1 ACTIVOS', '1 ACTIVOS'), ('2 PENSIONADOS', '2 PENSIONADOS'),
                   ('3 JUBILADO ANTICIPADO', '3 JUBILADO ANTICIPADO'), ('4 APRENDICES', '4 APRENDICES'),
                   ('5 RETIRADOS', '5 RETIRADOS'),
                   ('7 TEMPORALES', '7 TEMPORALES'), ('9 EXTERNOS', '9 EXTERNOS'), ]

SELECTION_LABOR = [('01 LEY 50', '01 LEY 50'), ('02 REG ANTERIOR', '02 REG ANTERIOR'), ('03 INTEGRAL', '03 INTEGRAL'),
                   ('04 APRENDIZAJE', '04 APRENDIZAJE'), ('05 PENSIONADO', '05 PENSIONADO'),
                   ('06 EXTERNO/TEMPOR', '06 EXTERNO/TEMPOR')]


class HrEmployeeSubstitution(models.Model):
    _name = 'hr.employee.substitution'
    _description = 'Hr Employee Substitution'

    currency_id = fields.Many2one('res.currency', related='current_company_id.currency_id')

    name = fields.Char(copy=False, default=lambda self: _('New'))
    current_company_id = fields.Many2one('res.company', 'Current Company', default=lambda self: self.env.company,
                                         required=True)
    new_company_id = fields.Many2one('res.company', 'New Company', required=False)

    state = fields.Selection(selection=STATE, string='State', default='draft')
    creation_date = fields.Date('Creation Date', default=date.today())
    validation_date = fields.Date('Validation Date')

    employee_id = fields.Many2one('hr.employee', 'Employee')
    identification_id = fields.Char('No. Identification')
    contract_id = fields.Many2one('hr.contract')
    wage = fields.Monetary('Wage', related='contract_id.wage')

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')

    current_arl_percentage = fields.Float('ARL Percentage', digits=(32, 6))
    new_arl_percentage = fields.Float('New ARL Percentage', digits=(32, 6))
    current_resource_calendar_id = fields.Many2one('resource.calendar', 'Current Work planning')
    new_resource_calendar_id = fields.Many2one('resource.calendar', 'New Work planning')

    """Center Cost"""
    current_center_cost_id = fields.One2many('hr.center.cost', 'employee_substitution_id', string='Current cost center')
    new_center_cost_id = fields.One2many('hr.new.center.cost', 'employee_substitution_id', string='New cost center')

    """Boolean Fields"""
    check_cost_center = fields.Boolean('Change of Cost Center?')
    check_salary = fields.Boolean('Salary Change?')

    """New Field Boolean"""
    check_job = fields.Boolean('Job Position')
    check_division = fields.Boolean('change division?')

    """New Fields"""
    new_salary = fields.Float()
    new_salary_fixed = fields.Float()
    current_flex_wage_ids = fields.One2many(
        related='contract_id.flex_wage_ids', string='Current Flex Wage')
    new_flex_wage_ids = fields.One2many(
        'hr.contract.flex_wage', 'hr_employee_substitution_id',
        string='New Flex Wage')
    current_job_id = fields.Many2one(related='employee_id.job_id')
    new_job_id = fields.Many2one('hr.job', 'New Job Position')

    """Arl"""
    current_arl_id = fields.Many2one('res.partner', 'Current Arl')
    new_arl_id = fields.Many2one('res.partner', 'Current Arl', domain=[("is_arl", '=', True)])

    """Organization Unit"""
    current_organization_unit_id = fields.Many2one('hr.employee.unit', 'Current Organization Unit')
    new_organization_unit_id = fields.Many2one('hr.employee.unit', 'New Organization Unit')

    """Contract Type"""
    current_contract_type_id = fields.Many2one('hr.contract.type', 'Current contract type')
    new_contract_type_id = fields.Many2one('hr.contract.type', 'New contract type')

    """Fields Sysman"""
    current_division_id = fields.Many2one('hr.employee.division', 'Current Division')
    new_division_id = fields.Many2one('hr.employee.division', 'New Division')
    current_salary_type = fields.Selection([
        ('SUELDO BÁSICO', 'SUELDO BÁSICO'),
        ('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),
        ('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],
        string='Current Contract Salary Type',
        tracking=True)

    new_salary_type = fields.Selection([
        ('SUELDO BÁSICO', 'SUELDO BÁSICO'),
        ('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),
        ('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],
        string='New Contract Salary Type',
        tracking=True)

    current_grupo_seleccion_emp = fields.Selection(selection=SELECTION_GROUP, string='Grupo de Personal Actual')
    new_grupo_seleccion_emp = fields.Selection(selection=SELECTION_GROUP, string='Nuevo Grupo de Personal')

    current_relacion_laboral_emp = fields.Selection(selection=SELECTION_LABOR, string='Relación Laboral Actual')
    new_relacion_laboral_emp = fields.Selection(selection=SELECTION_LABOR, string='Relación Laboral Actual')

    current_personal_area_id = fields.Many2one('hr.employee.area', 'Area Personal Actual')
    new_personal_area_id = fields.Many2one('hr.employee.area', 'Nueva Area Personal Actual')

    current_ccf_id = fields.Many2one('res.partner', 'Current CCF')
    new_ccf_id = fields.Many2one('res.partner', 'New CCF', domain=[('is_ccf', '=', True)])

    @api.model
    def create(self, vals):
        """Create Sequence."""
        res = super(HrEmployeeSubstitution, self).create(vals)
        if res.current_company_id:
            res.name = self.env['ir.sequence'].with_company(
                res.current_company_id).next_by_code(
                'hr.employee.substitution') or _('New')
        else:
            res.name = self.env['ir.sequence'].next_by_code(
                'hr.employee.substitution') or _('New')
        return res

    """Onchange Methods"""

    @api.onchange('identification_id')
    def onchange_identification_id(self):
        self.employee_id = False
        if self.identification_id:
            employee = self.env['hr.employee'].search(
                [('identification_id', '=', self.identification_id),
                 ('company_id.id', '=', self.current_company_id.id)], limit=1)
            if employee:
                self.employee_id = employee.id

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.identification_id = False
        if self.employee_id:
            self.identification_id = self.employee_id.identification_id
            self.current_division_id = self.employee_id.division_id
            self.current_grupo_seleccion_emp = self.employee_id.grupo_seleccion_emp
            self.current_relacion_laboral_emp = self.employee_id.relacion_laboral_emp
            self.current_personal_area_id = self.employee_id.personal_area_id
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('active', '=', True), ('state', '=', 'open')], limit=1)
            if contract:
                self.contract_id = contract.id
                self.current_center_cost_id = contract.center_cost_ids
                self.current_arl_percentage = contract.arl_percentage
                self.current_salary_type = contract.salary_type
                self.current_resource_calendar_id = contract.resource_calendar_id

    """Button Methods"""

    def process(self):
        if self.state == 'draft':
            self.state = 'processed'

    def cancel(self):
        if self.state == 'processed':
            self.state = 'cancel'

    def completed(self):
        if self.state == 'processed':
            self.state = 'completed'
            self.validation_date = date.today()
            new_employee = False
            new_contract = False
            if self.employee_id:
                new_employee = self.employee_id.copy()
                new_employee.write({
                    'name': self.employee_id.name,
                    'is_employer_substitution': True,
                    'address_id': self.new_company_id.partner_id,
                    'company_id': self.new_company_id.id})
                new_employee.check_employer_substitution()
                if self.contract_id:
                    new_contract = self.contract_id.copy()
                    new_contract.write({
                        'company_id': self.new_company_id.id,
                        'employee_id': new_employee.id})

                    if self.new_salary:
                        new_contract.write({'wage': self.new_salary})

                    if self.new_arl_percentage:
                        new_contract.write({'arl_percentage': self.new_arl_percentage})

                    if self.new_salary_type:
                        new_contract.write({'salary_type': self.new_salary_type})

                    if self.new_division_id:
                        new_employee.write({'division_id': self.new_division_id})

                    if self.new_grupo_seleccion_emp:
                        new_employee.write({'grupo_seleccion_emp': self.new_grupo_seleccion_emp})

                    if self.new_personal_area_id:
                        new_employee.write({'personal_area_id': self.new_personal_area_id})

                    if self.new_relacion_laboral_emp:
                        new_employee.write({'relacion_laboral_emp': self.new_relacion_laboral_emp})

                    if self.new_job_id:
                        new_employee.write({'job_id': self.new_job_id.id})
                        new_contract.write({'job_id': self.new_job_id.id})

                    if self.new_salary_fixed:
                        new_contract.write({
                            'fix_wage_amount': self.new_salary_fixed})

                    if self.new_flex_wage_ids:
                        new_contract.write({'flex_wage_ids': [(5, 0, 0)]})
                        for flex in self.new_flex_wage_ids:
                            self.env['hr.contract.flex_wage'].create({
                                'salary_rule_id': flex.salary_rule_id.id,
                                'fixed': flex.fixed,
                                'amount': flex.amount,
                                'percentage': flex.percentage,
                                'contract_id': new_contract.id})

                    if self.new_center_cost_id:
                        for cost_ce_rec in self.new_center_cost_id:
                            self.env['hr.center.cost'].create({
                                'name': cost_ce_rec.name,
                                'percent': cost_ce_rec.percent,
                                'account_analytic_id': cost_ce_rec.account_analytic_id.id,
                                'request_news_id': cost_ce_rec.request_news_id.id,
                                'direct_indirect': cost_ce_rec.direct_indirect,
                                'contract_id': new_contract.id,
                                'employee_id': new_employee.id
                            })

                    if new_employee and new_contract:
                        for payroll in self.env['hr.payslip'].search([
                            ('employee_id', '=', self.employee_id.id),
                            ('state', 'in', ['paid', 'done'])]):
                            payslip = self.env['hr.payslip'].create({
                                'employee_id': new_employee.id,
                                'date_from': payroll.date_from,
                                'date_to': payroll.date_to,
                                'name': new_employee.name,
                                'contract_id': new_contract.id,
                                'company_id': self.new_company_id.id
                            })
                            payslip._onchange_employee()

                        for pv in self.env['hr.pv'].search([
                            ('employee_id', '=', self.employee_id.id),
                            ('state', 'in', ['approved', 'processed'])]):
                            self.env['hr.pv'].create({
                                'event_id': pv.event_id.id,
                                'employee_id': new_employee.id,
                                'start_date': pv.start_date,
                                'end_date': pv.end_date,
                                'amount': pv.amount,
                                'percentage': pv.percentage,
                                'company_id': self.new_company_id.id
                            })

                        for dis_aid in self.env['hr.payroll.dis.aid'].search([
                            ('employee_id', '=', self.employee_id.id), ('state', '=', 'approved')]):
                            dis_aid_new = dis_aid.copy()
                            dis_aid_new.write({
                                'employee_id': new_employee.id,
                                'company_id': self.new_company_id.id,
                                'terms_in_months': dis_aid.quote_to_pay,
                                'total': dis_aid.capital_to_pay,
                            })

                            dis_aid_new.action_approve()
                            dis_aid.action_finish()

                        self.contract_id.write({'state': 'close'})
                        self.employee_id.write({'active': False})
