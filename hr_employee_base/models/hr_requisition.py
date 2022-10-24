# -*- coding: utf-8 -*-
from random import randint

from odoo import fields,models,api,_
from odoo.exceptions import ValidationError


class HrRequisition(models.Model):
    _name = 'hr.requisition'
    _description = 'Requisiciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _mailing_enabled = True

    

    def _default_stage(self):
        return self.env['hr.requisition.stage'].search([('id', '>', 0), ('active', '=', True)], order='sequence', limit=1)


    def _default_approval_ids(self):
        stages = self.env['hr.requisition.stage'].search([("active","=", True), ("stage_type", "in", ["open", "approval","process"])])
        approvals = [(
                0,
                0,
                {
                    "stage_id": stage.id,
                    "approver_id": stage.approver_id.id if stage.approver_id else False,
                    "requisition_id": self.id
                }
            ) for stage in stages]
        return approvals

    state = fields.Char('Estado', related='stage_id.name')
    stage_id = fields.Many2one('hr.requisition.stage', 'Estado', copy=False, default=_default_stage,  tracking=True, required=True, group_expand='_expand_stages')

    name = fields.Char('Requisición', tracking=True)
    requesting_employee = fields.Many2one('hr.employee', string='Solicitante', tracking=True)
    requesting_employee_job = fields.Char(string='Cargo del Solicitante', related='requesting_employee.job_id.display_name',tracking=True)
    company_id = fields.Many2one('res.company', 'Compañía', required=True, readonly=True, tracking=True, default=lambda self: self.env.company )

    priority = fields.Selection([('low', 'Baja'),('medium', 'Media'),('high', 'Alta'),('very_high', 'Muy alta')], tracking=True)
    opening_date = fields.Datetime(string='Fecha de Apertura', copy=False, required=True, readonly=True, index=True,  default = fields.Datetime.now,   help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    approve_date = fields.Datetime(string='Fecha de Aprobación', copy=False, readonly=True, index=True)
    reject_date = fields.Datetime(string='Fecha de Rechazo', copy=False, readonly=True, index=True)
    immediate_boss_id = fields.Many2one('hr.employee', string="Jefe Inmediato", tracking=True)

    job_id = fields.Many2one('hr.job', string="Cargo Solicitado", tracking=True)
    primary_education_level = fields.Selection(string='Nivel educativo', related='job_id.nivel_primario_educativo_minimo')
    advanced_education_level = fields.Selection(string='Nivel educativo avanzado', related='job_id.nivel_secundario_educativo')
    job_role_id = fields.Many2one('hr.job.role', string="Rol del cargo", tracking=True)
    skill_ids = fields.Many2many('hr.skill', string='Habilidades')

    vacancies_qty = fields.Integer(string="Cantidad de Vacantes",tracking=True)
    gender = fields.Selection([('MASCULINO', 'MASCULINO'),('FEMENINO', 'FEMENINO'),('INDIFERENTE', 'INDIFERENTE')], "Género", default="INDIFERENTE", tracking=True)

    city_id = fields.Many2one('res.city','Ciudad', tracking=True)
    state_id = fields.Many2one('res.country.state', tracking=True)
    sede = fields.Char(string="Sede",tracking=True)
    area = fields.Char(string="Área",tracking=True)
    organizational_unit_id = fields.Many2one('hr.employee.unit','Unidad Organizativa',tracking=True)
    cost_center_id = fields.Many2one('hr.employee.cost.center', string='Centro de costo', tracking=True)

    in_charge_of_personnel = fields.Boolean('Tiene Personal a Cargo', tracking=True)
    interview_required = fields.Boolean(string="Requiere Entrevista",tracking=True)
    test_required = fields.Boolean(string="Requiere Prueba Técnica",tracking=True)
    security_check_required = fields.Boolean(string="Requiere Estudio de Seguridad",tracking=True)

    work_shift_id = fields.Many2one("hr.employee.shift.type",'Turno',tracking=True)
    resource_calendar_id = fields.Many2one('resource.calendar','Horario',tracking=True)
    arl_risk = fields.Float(related="risk_type_id.percentage", string="Porcentaje Nivel de Riesgo",tracking=True)

    arl_risk_level = fields.Selection([('1 RIESGO I', '1 RIESGO I'),('2 RIESGO II', '2 RIESGO II'),('3 RIESGO III','3 RIESGO III'),('4 RIESGO IV','4 RIESGO IV'),('5 RIESGO V','5 RIESGO V')],tracking=True)
    risk_type_id = fields.Many2one('hr.risk.type', string='Nivel de Riesgo')

    disability_handling_id = fields.Many2one("hr.disability.handling",string="Manejo de Incapacidades",tracking=True)

    req_motive_id = fields.Many2one("hr.recruitment.reason",string="Motivo Solicitud", domain="[('requisition_reason', '=', True)]")
    employee_replace = fields.Many2one('hr.employee',string="Persona a quien reemplaza",tracking=True)
    budgeted_job = fields.Boolean('Cargo Presupuestado',tracking=True)

    #informacion del salario y contrato//
    salary_type = fields.Selection([('SUELDO BÁSICO', 'SUELDO BÁSICO'),('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],string="Tipo de Salario",tracking=True)
    wage = fields.Monetary('Salario', required=True, currency_field='currency_id', tracking=True, help="Employee's monthly gross wage.")
    wage_max = fields.Monetary('Salario máximo', required=True, currency_field='currency_id', tracking=True)
    currency_id = fields.Many2one(string="Moneda", related='company_id.currency_id', readonly=True)
    agreement = fields.Selection([('PACTO COLECTIVO', 'PACTO COLECTIVO'),('CONVENCIÓN COLECTIVA DE TRABAJO', 'CONVENCIÓN COLECTIVA DE TRABAJO'),('NO APLICA','NO APLICA')],'Pacto/Convención',tracking=True)
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipo de Contrato', tracking=True)
    # contract_type = fields.Selection([('FIJO', 'FIJO'),('MEDIO TIEMPO','MEDIO TIEMPO'),('SERVICIOS', 'SERVICIOS'),('INDEFINIDO', 'INDEFINIDO'),('OBRA LABOR', 'OBRA LABOR'),('APRENDIZAJE', 'APRENDIZAJE'),('DIARIO','DIARIO')])
    client = fields.Char(string="Cliente",tracking=True)
    contract_number = fields.Char(string="No. Contrato Comercial",tracking=True)
    initial_contract_time = fields.Integer(string="Tiempo de Contrato Inicial",tracking=True)
    contract_time_range = fields.Selection([('DÍAS', 'DÍAS'),('MESES', 'MESES'),('AÑOS', 'AÑOS')],string="Rango",tracking=True)

    referral_document = fields.Binary(string="Documento Referido",tracking=True)
    color = fields.Integer(string='Color Index', default=lambda self: randint(1, 11))
    #auxilios
    food_allowance = fields.Boolean('Auxilio de Alimentación Fijo',tracking=True)
    food_allowance_value = fields.Float(string="Valor Auxilio de Alimentación",tracking=True, default=0)
    food_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],string="Auxilio de Alimentación Fijo a partir de",tracking=True)
    food_allowance_proportional = fields.Boolean('Auxilio de Alimentación Proporcional',tracking=True)
    food_allowance_proportional_value = fields.Float(tracking=True,string="Valor Auxilio de Alimentación Proporcional", default=0)
    food_allowance_proportional_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],string="Auxilio de Alimentación Proporcional a partir de",tracking=True)
    transport_allowance = fields.Boolean(string="Auxilio de Rodamiento Fijo",tracking=True)
    transport_allowance_value = fields.Float(string="Valor Auxilio de Rodamiento",tracking=True, default=0)
    transport_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
    transport_allowance_proportional = fields.Boolean(string="Auxilio de Rodamiento Proporcional",tracking=True)
    transport_allowance_proportional_value = fields.Float(string="Valor Auxilio de Rodamiento Proporcional",tracking=True, default=0)
    transport_allowance_proportional_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],string="Auxilio de Rodamiento Proporcional a partir de",tracking=True)
    cellphone_allowance = fields.Boolean(string="Auxilio de Celular",tracking=True)
    cellphone_allowance_value = fields.Float(string="Valor Auxilio de Celular",tracking=True, default=0)
    cellphone_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')], string="Auxilio de Celular a partir de", tracking=True)
    mobilization_allowance = fields.Boolean(string="Auxilio de Movilización",tracking=True)
    mobilization_allowance_value = fields.Float(string="Valor Auxilio de Movilización",tracking=True,  default=0)
    mobilization_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],string="Auxilio de Movilización a partir de",tracking=True)

    #campos Beneficios
    prepaid_medicine = fields.Boolean(string="Medicina Prepagada",tracking=True)
    prepaid_medicine_value = fields.Float(string="Valor Medicina Prepagada", tracking=True)
    prepaid_medicine_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')], string="Bonos a partir de", tracking=True)
    bonos = fields.Boolean(tracking=True)
    bono_value = fields.Float(string="Valor Bonos",tracking=True, default=0)
    bonos_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
    commission = fields.Boolean("Comisiones",tracking=True)
    commission_value = fields.Float(string="Valor Comisiones", default=0)
    commission_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')], string="Comisiones a partir de",tracking=True)
    other_benefit = fields.Char("Otro beneficio", tracking=True)
    other_benefit_value = fields.Float("Valor Otro beneficio",tracking=True, default=0)
    other_benefit_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],string="Otro beneficio a partir de",tracking=True)
    job_type_id = fields.Many2one('hr.job.type', string="Tipo cargo")
    observations = fields.Text(string="Observaciones",tracking=True)
    req_therapist = fields.Many2one('res.users', string="Psicologo",tracking=True)
    req_recruiter = fields.Many2one('res.users', string="Reclutador",tracking=True)

    applicant_count = fields.Integer('Number of sheets', compute='_compute_applicant_data')
    applicant_ids = fields.One2many('hr.applicant','requisition_id')
    #aprobaciones//
    approval_ids = fields.One2many('hr.requisition.approval', 'requisition_id', string='Aprobaciones', default=_default_approval_ids)
    #nombre y ID de la etapa
    recruitment_stage_type = fields.Selection(related="stage_id.stage_type")
    recruitment_stage_seq = fields.Integer(related="stage_id.sequence")

    # no_of_hired_employee
    no_of_hired_employee = fields.Integer('Hired Employees', compute='_compute_no_of_hired_employee')

    def _compute_no_of_hired_employee(self):
        for record in self:
            record.no_of_hired_employee = len(self.env['hr.employee'].search([('requisition_id','=',record.id)]))

    def _compute_applicant_data(self):
        for record in self:
            count = len(record.applicant_ids)
            record.applicant_count = count

    def action_view_applicant(self):
        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job').read()[0]
        action['context'] = {
            'default_requisition_id': self.id,
        }
        action['domain'] = [('requisition_id', '=', self.id)]
        return action

    def _expand_stages(self, stage_id, domain, order):
        stage_id = self.env['hr.requisition.stage'].search([("active","=", True)])
        return stage_id

    @api.constrains('vacancies_qty')
    def _check_can_vacantes(self):
        for record in self:
            if record.vacancies_qty <= 0:
                raise ValidationError("La Cantidad de Vacantes no puede ser 0  : %s" % record.vacancies_qty)


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('requisiciones') or _('Nuevo')
        vals.update()
        result = super(HrRequisition, self).create(vals)
        return result

    #funciones de los botones para cambiar de estados.
    def button_approved(self):
        if self.stage_id.stage_type == "rejection":
            approval = self.approval_ids.filtered(lambda a: a.state=="rejected")
            stage = approval.stage_id._next_stage() or approval.stage_id.search(
                [
                    ("active", "=", True),
                    ("stage_type", "=", "application")
                ], order='sequence', limit=1
            )
        else :
            stage = self.stage_id._next_stage()
            approval = self.approval_ids.filtered(lambda a: a.stage_id==self.stage_id)
            
        approval.write({
            'state': approval._get_approval_state(),
            'response_date': fields.Datetime.now(),
        })
        self.write({
            'stage_id': stage.id,
            'approve_date': fields.Datetime.now(),
            'reject_date': False,
        })
    
    def button_rejected(self):
        stage = self.stage_id._next_stage(rejected=True)
        if stage:
            approval = self.approval_ids.filtered(lambda a: a.stage_id==self.stage_id)
            approval.write({
                'state': 'rejected',
                'response_date': fields.Datetime.now(),
            })
            if self.stage_id.stage_type == "application":
                last_approval = self.approval_ids.filtered(lambda a: a.state=='approved')[-1]
                last_approval.write({
                    'state': 'rejected',
                    'response_date': fields.Datetime.now(),
                })
            self.write({
                'stage_id': stage.id,
                'reject_date': fields.Datetime.now(),
                'approve_date': False
            })

class HrRequitionStage(models.Model):
    _name = 'hr.requisition.stage'
    _order='sequence'
    _description = 'Requisition stage'

    name = fields.Char("Nombre")
    sequence = fields.Integer("sequence", default=1)
    active = fields.Boolean('active', default=True)
    applicant_stage = fields.Boolean('Estado de Aplicación')
    approver_id = fields.Many2one('hr.employee', string='Aprobador Fijo',
        help="Fill If requisition stage has a fixed approver")
    stage_type = fields.Selection([
        ('open', 'Apertura'),
        ('approval', 'Aprobación'),
        ('process', 'Proceso'),
        ('rejection', 'Rechazo'),
        ('application', 'Postulación')
    ], default="approval", string='Tipo Etapa')

    def _next_stage(self, rejected=False):
        if rejected:
            stage = self.search(
            [
                ("active", "=", True),
                ("stage_type", "=", "rejection")
            ], order='sequence', limit=1)
        else:
            stage = self.search(
                [
                    ("id", "!=", self.id),
                    ("active", "=", True),
                    ("sequence", ">", self.sequence),
                    ("stage_type", "in", ["approval", "process", "application"])
                ],
                order='sequence',
                limit=1
            )
        return stage

class HrRequisitonApproval(models.Model):
    _name = 'hr.requisition.approval'
    _description = 'Requisition Approvals'
    _rec_name = 'stage_id'

    stage_id = fields.Many2one('hr.requisition.stage', string='Stage')
    requisition_id = fields.Many2one('hr.requisition', string='Requisition')
    approver_id = fields.Many2one('hr.employee', string='Approver')
    state = fields.Selection([
        ('done', 'Realizado'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado')
    ], string='Approval state')
    response_date = fields.Datetime("Response Date")

    def _get_approval_state(self):
        states = {
            'open': 'approved',
            'approval': 'approved',
            'process': 'done',
        }
        return states.get(self.stage_id.stage_type, False)
 