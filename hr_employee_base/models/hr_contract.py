# -*- coding: utf-8 -*-
from odoo import fields,models,api,_ 

class HrContract(models.Model):
   _inherit = 'hr.contract'

   #campos relacionados del empleado//
   employee = fields.Many2one('hr.employee',string="Empleado",tracking=True)
   employe_identification = fields.Char(related="employee_id.identification_id")   
   employee_phone = fields.Char(related="employee_id.phone")
   employee_email = fields.Char(related="employee_id.private_email")
   work_email = fields.Char()
   work_phone = fields.Char()
   employee_full_address = fields.Char(related="employee_id.full_address") 
   employee_id = fields.Many2one('hr.employee', required="True")
   job_id = fields.Many2one('hr.job', string="Puesto de Trabajo", required="True")
   #campos relacionados de la requisición//
   requisition_id = fields.Many2one(related="employee_id.requisition_id",tracking=True)
   initial_contract_time = fields.Integer(tracking=True)
   contract_time_range = fields.Selection([('DÍAS', 'DÍAS'),('MESES', 'MESES'),('AÑOS', 'AÑOS')],tracking=True)
   contract_number = fields.Char(tracking=True)
   contract_type_id = fields.Many2one('hr.contract.type', string='Contract Type', tracking=True)   
   work_shift_id=fields.Many2one("hr.employee.shift.type",'Turno',tracking=True)
   req_area=fields.Char(related="requisition_id.area",tracking=True)
   # vacation_handling=fields.Selection([('L-V', 'L-V'),('L-S', 'L-S')],tracking=True)
   disability_handling_id = fields.Many2one("hr.disability.handling", string="Manejo de Incapacidades", tracking=True)
   salary_type = fields.Selection([('SUELDO BÁSICO', 'SUELDO BÁSICO'),('SALARIO INTEGRAL', 'SALARIO INTEGRAL'),('APOYO SOSTENIMIENTO', 'APOYO SOSTENIMIENTO')],tracking=True)
   agreement = fields.Selection([('PACTO COLECTIVO', 'PACTO COLECTIVO'),('CONVENCIÓN COLECTIVA DE TRABAJO', 'CONVENCIÓN COLECTIVA DE TRABAJO'),('NO APLICA','NO APLICA')],tracking=True)
   food_allowance = fields.Boolean(tracking=True)
   food_allowance_value = fields.Float(string="Valor Auxilio de Alimentación",tracking=True, default=0)
   food_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
   food_allowance_proportional = fields.Boolean(tracking=True)
   food_allowance_proportional_value = fields.Float(tracking=True, default=0) 
   food_allowance_proportional_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)    
   transport_allowance = fields.Boolean(tracking=True)
   transport_allowance_value = fields.Float(string="Valor Auxilio de Rodamiento",tracking=True, default=0)
   transport_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
   transport_allowance_proportional = fields.Boolean(tracking=True)
   transport_allowance_proportional_value = fields.Float(tracking=True, default=0)
   transport_allowance_proportional_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
   cellphone_allowance = fields.Boolean(tracking=True)
   cellphone_allowance_value = fields.Float(string="Valor Auxilio de Celular",tracking=True, default=0)
   cellphone_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
   mobilization_allowance = fields.Boolean(tracking=True)
   mobilization_allowance_value = fields.Float(tracking=True,  default=0)
   mobilization_allowance_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)    
   prepaid_medicine = fields.Boolean(tracking=True)
   prepaid_medicine_value = fields.Float(string="Valor Medicina Prepagada", tracking=True)
   prepaid_medicine_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True) 
   bonos=fields.Boolean(tracking=True)
   bono_value=fields.Float(string="Valor Bonos",tracking=True, default=0)
   bonos_start=fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True) 
   commission = fields.Boolean(tracking=True)
   commission_value = fields.Float(string="Valor Comisiones", default=0)
   commission_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True) 
   other_benefit = fields.Char(tracking=True)
   other_benefit_value = fields.Float(tracking=True, default=0)
   other_benefit_start = fields.Selection([('FECHA DE INGRESO', 'FECHA DE INGRESO'),('1 MES', '1 MES'),('2 MESES','2 MESES'),('3 MESES','3 MESES'),('4 MESES','4 MESES')],tracking=True)
   client = fields.Char(tracking=True)
   risk_type_id = fields.Many2one('hr.risk.type', string='Nivel de Riesgo')
   arl_risk_level = fields.Selection([('1 RIESGO I', '1 RIESGO I'),('2 RIESGO II', '2 RIESGO II'),('3 RIESGO III','3 RIESGO III'),('4 RIESGO IV','4 RIESGO IV'),('5 RIESGO V','5 RIESGO V')],tracking=True)
   arl_risk = fields.Selection([('0.522%', '0.522%'),('1.044%', '1.044%'),('2.436%', '2.436%'),('4.350%', '4.350%'),('6.960%','6.960%')],tracking=True)
   #campos grupo:representante//
   responsible_employee = fields.Many2one('hr.employee',tracking=True)
   responsible_document = fields.Char(related="responsible_employee.identification_id")
   responsible_job_id = fields.Many2one(related="responsible_employee.job_id",tracking=True)
   responsible_expedition_city = fields.Many2one(related="responsible_employee.expedition_city_id")
   employee_expedition_city = fields.Many2one(related="employee_id.expedition_city_id")
   #campos grupo:terminos de contrato
   city_id = fields.Many2one('res.city',string="Ciudad",tracking=True)
   immediate_boss = fields.Many2one('hr.employee',string="Jefe Inmediato")
   immediate_boss_job = fields.Many2one(related="immediate_boss.job_id")
   trial_days = fields.Integer(tracking=True)
   #grupo
   pay_mode = fields.Char(default='TRANSFERENCIA')   
   requesting_employee = fields.Many2one(related="requisition_id.requesting_employee", string="Solicitante")
   #campo fecha firma
   firma_date = fields.Date()
   #campos grupo: aprendiz Sena
   trainee_type = fields.Selection([('ETAPA LECTIVA', 'ETAPA LECTIVA'),('ETAPA PRODUCTIVA', 'ETAPA PRODUCTIVA'),('PRACTICANTE', 'PRACTICANTE UNIVERSITARIO')],tracking=True)
   teaching_stage_end_date=fields.Date(tracking=True)
   productive_stage_start_date=fields.Date(tracking=True)
   productive_stage_end_date=fields.Date(tracking=True)   
   #horario
   resource_calendar_id=fields.Many2one('resource.calendar',tracking=True)
   #cuenta bancaria
   employee_bank_account=fields.Many2one(related="employee_id.bank_account_id",tracking=True)
   #version del documento
   document_version=fields.Char(tracking=True, default="-V")
   #dirrecion del empleado
   addressm_id = fields.Many2one('hr.employee.address', string="Vía Principal", related="employee_id.addressm_id")
   main_road = fields.Char(string="Nombre Vía Principal", related="employee_id.main_road")
   generator_road = fields.Char(string="Vía Generadora", related="employee_id.generator_road")
   land = fields.Char(string="Predio", related="employee_id.land")
   road_complement = fields.Char(string="Complemento", related="employee_id.road_complement")
   #imagen para firma
   firma = fields.Binary(string="Firma")
   benefit_type_value = fields.Float(string="Importe Clase Beneficio", related="employee_id.benefit_type_value")
  
        

   #Función para llevar información de requisiciones a contratos - 
   @api.onchange('requisition_id')
   def _onchange_requisicion(self):
      if self.requisition_id:
         self.contract_type_id =  self.requisition_id.contract_type_id.id
         self.initial_contract_time =  self.requisition_id.initial_contract_time
         self.contract_time_range =  self.requisition_id.contract_time_range
         self.contract_number =  self.requisition_id.contract_number
         self.work_shift_id =  self.requisition_id.work_shift_id.id
         self.resource_calendar_id =  self.requisition_id.resource_calendar_id.id
         self.disability_handling_id = self.requisition_id.disability_handling_id.id
         self.risk_type_id = self.requisition_id.risk_type_id.id
         self.salary_type = self.requisition_id.salary_type
         self.agreement = self.requisition_id.agreement
         self.food_allowance = self.requisition_id.food_allowance
         self.food_allowance_value = self.requisition_id.food_allowance_value
         self.food_allowance_start = self.requisition_id.food_allowance_start
         self.food_allowance_proportional = self.requisition_id.food_allowance_proportional
         self.food_allowance_proportional_value = self.requisition_id.food_allowance_proportional_value
         self.food_allowance_proportional_start = self.requisition_id.food_allowance_proportional_start
         self.transport_allowance = self.requisition_id.transport_allowance
         self.transport_allowance_start = self.requisition_id.transport_allowance_start
         self.transport_allowance_proportional = self.requisition_id.transport_allowance_proportional
         self.transport_allowance_proportional_start = self.requisition_id.transport_allowance_proportional_start
         self.cellphone_allowance = self.requisition_id.cellphone_allowance
         self.cellphone_allowance_value = self.requisition_id.cellphone_allowance_value
         self.cellphone_allowance_start = self.requisition_id.cellphone_allowance_start
         self.mobilization_allowance = self.requisition_id.mobilization_allowance
         self.mobilization_allowance_value = self.requisition_id.mobilization_allowance_value
         self.mobilization_allowance_start = self.requisition_id.mobilization_allowance_start
         self.prepaid_medicine = self.requisition_id.prepaid_medicine
         self.prepaid_medicine_value = self.requisition_id.prepaid_medicine_value
         self.prepaid_medicine_start = self.requisition_id.prepaid_medicine_start
         self.bonos = self.requisition_id.bonos
         self.bono_value = self.requisition_id.bono_value
         self.bonos_start = self.requisition_id.bonos_start
         self.commission = self.requisition_id.commission
         self.commission_value = self.requisition_id.commission_value
         self.commission_start = self.requisition_id.commission_start
         # self.otro = self.requisition_id.otro
         self.other_benefit = self.requisition_id.other_benefit
         self.other_benefit_value = self.requisition_id.other_benefit_value
         self.other_benefit_start = self.requisition_id.other_benefit_start
         self.wage = self.requisition_id.wage
         self.client = self.requisition_id.client
         self.immediate_boss = self.requisition_id.immediate_boss_id.id
         self.city_id = self.requisition_id.city_id.id
         
class HrContractType(models.Model):
   _name = 'hr.contract.type'
   _description = 'Contract Type'

   name = fields.Char('Name', required=True)
   description = fields.Text('Description')
   date_end_required = fields.Boolean()
   trial_period_duration = fields.Integer(copy=False)
   is_labor_contract = fields.Boolean('Contrato de obra o labor')