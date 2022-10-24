# -*- coding: utf-8 -*-

import re
import base64
from datetime import datetime
from odoo import fields,models,api
from odoo.exceptions import ValidationError


tallazapatos = [
    ('30', '30'),
    ('31', '31'),
    ('32', '32'),
    ('33', '33'),
    ('34', '34'),
    ('35', '35'),
    ('36', '36'),
    ('37', '37'),
    ('38', '38'),
    ('39', '39'),
    ('40', '40'),
    ('41', '41'),
    ('42', '42'),
    ('43', '43'),
    ('44', '44')
]

grupo_san = [
    ('a+', 'A+'),
    ('a-', 'A-'),
    ('b+', 'B+'),
    ('b-', 'B-'),
    ('ab+', 'AB+'),
    ('ab-', 'AB-'),
    ('o+', 'O+'),
    ('o-', 'O-')
]

property_type_list = [
    ('rented', 'ARRENDADO'),
    ('community', 'COMUNITARIA'),
    ('family', 'FAMILIAR'),
    ('own', 'PROPIA'),
    ('other', 'OTRO')
]




class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    # One2many
    education_ids = fields.One2many('hr.employee.education','applicant_id','Formación')   
    son_ids = fields.One2many('hr.employee.son', 'applicant_id', 'Hijos')
    pet_ids = fields.One2many('hr.employee.pet','applicant_id', 'Mascotas')
    lang_ids = fields.One2many('hr.employee.lang','applicant_id','Idiomas')
    #campos del grupo 1 page informacion general 
    first_surname = fields.Char(string="Primer Apellido", tracking=1)
    second_surname = fields.Char(string="Segundo Apellido", tracking=2)
    first_name = fields.Char(string="Primer Nombre", tracking=3)
    second_name = fields.Char(string="Segundo Nombre", tracking=4)
    treatment_id = fields.Many2one('res.partner.title', string='Tratamiento')
    nit = fields.Char(string='NIT', size=11, tracking=5)
    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type', string='Tipo de documento', tracking=5)
    identification_id = fields.Char(string="Número de Identificación")
    confirm_id = fields.Char(string="Confirmar Número de Identificación")
    expedition_city_id = fields.Many2one('res.city')
    promotion = fields.Boolean(tracking=True)
    data_treatment = fields.Boolean()
    description = fields.Text(invisible="True")
    emal_cc = fields.Char('Confirmar correo electrónico')
    #Campos de Dirección. tipo DIAN   
    addressm_id = fields.Many2one('hr.employee.address',tracking=True)
    main_road = fields.Char('Nombre Via Principal',tracking=True)
    generator_road = fields.Char(tracking=True)
    land = fields.Char(tracking=True)
    road_complement = fields.Char(tracking=True)
    full_address = fields.Char(tracking=True)
    #campos grupo 2 de la page informacion general
    country_id = fields.Many2one('res.country',tracking=True)
    birth_date = fields.Date(string="Fecha de Nacimiento")
    place_of_birth = fields.Char()
    confirm_birthdate = fields.Date(string="Confirmar Fecha de Nacimiento")    
    state_id = fields.Many2one('res.country.state', 'Departamento',tracking=True)
    city_id = fields.Many2one('res.city','Ciudad', tracking=True)
    neighborhood = fields.Char(string="Barrio de Residencia", tracking=True)     
    #coat_size, pantalon, camisa, saco, zapatos
    pants_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')],'Talla Pantalón')
    shirt_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')], 'Talla Camisa')
    coat_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')], 'Talla Saco')
    shoes_size = fields.Selection(tallazapatos, 'Talla Zapatos', tracking=True)       
    #telefono,celular,correo,confirmar correo, idioma nativo, grupo sanguineo, gender. 
    native_lang_id = fields.Many2one('res.lang',tracking=True)
    blood_group = fields.Selection(grupo_san,'Grupo Sanguíneo')
    gender = fields.Selection([('male', 'Masculino'),('female', 'Femenino'), ('other', 'Otro')])
    declare_income = fields.Boolean(tracking=True)
    #GRUPO: INFORMACION DE VIVIENDA.
    property_type = fields.Selection(property_type_list,tracking=True)    
    other_property_type = fields.Char(tracking=True)
    house_type = fields.Selection([('CASA', 'CASA'),('APARTAMENTO', 'APARTAMENTO'),('HABITACIÓN', 'HABITACIÓN'),('OTRO','OTRO')],'Caracteristicas de la Vivienda',tracking=True)
    other_house_type = fields.Char(tracking=True)   
    house_zone = fields.Selection([('RURAL', 'RURAL'),('URBANA', 'URBANA'),('SUB', 'SUB URBANA')],tracking=True)
    energy_service = fields.Boolean('Cuenta con servicio de energía eléctrica',tracking=True)
    sewerage_service = fields.Boolean('Cuenta con Servicio de Alcantarillado',tracking=True)
    aqueduct_service = fields.Boolean('Cuenta con Servicio de Acueducto',tracking=True)
    #GRUPO: INFORMACION DE VIVIENDA2
    trash_service=fields.Boolean('Cuenta con servicio de recolección de basura',tracking=True)
    ethnic_group=fields.Selection([('Mestizo', 'MESTIZO'),('Blanco', 'BLANCO'),('Afrocolombiano', 'AFROCOLOMBIANO'),('Indigena','INDIGENA'),('Gitano','GITANO')],'Grupo Etnico',tracking=True)
    stratum=fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4','4'),('5','5'),('6','6')], string="Estrato Socioeconómico", tracking=True)
    gas_service=fields.Boolean('Cuenta con Servicio de Gas',tracking=True) 
    #campos: entidades del sistema de seguridad
    eps_partner_id=fields.Many2one('res.partner','EPS',tracking=True)
    afp_partner_id=fields.Many2one('res.partner','AFP',tracking=True)
    afc_partner_id=fields.Many2one('res.partner','AFC',tracking=True)

    #informacion parentesco
    contact_name=fields.Char(string="Nombre Completo",tracking=True)
    contact_phone=fields.Char(string="Télefono",tracking=True)
    relationship=fields.Selection([('ABUELO (A)', 'ABUELO (A)'),('AMIGO (A)', 'AMIGO (A)'),('ESPOSO (A)', 'ESPOSO (A)'),('HERMANO (A)','HERMANO (A)'),('PADRE','PADRE'),('MADRE','MADRE'),('SORBINO (A)','SOBRINO (A)'),('TIO (A)','TIO (A)'),('HIJO (A)','HIJO (A)'),('OTRO','OTRO')],tracking=True)
    other_relationship=fields.Char(tracking=True)
    contact_full_address=fields.Char(string="Dirección del contacto",tracking=True)
    contact_address_id=fields.Many2one('hr.employee.address','Vía Principal',tracking=True)
    contact_main_road=fields.Char('Nombre Vía Principal',tracking=True)
    contact_generator_road=fields.Char('Vía Generadora',tracking=True)
    contact_land=fields.Char('Predio',tracking=True)
    contact_road_complement=fields.Char(tracking=True)
    has_dependents=fields.Boolean('Tiene dependientes económicos',tracking=True)
    family_head=fields.Boolean('Es cabeza de familia',tracking=True)
    family_size=fields.Integer('No. de personas del nucleo familiar',tracking=True)
    disability_persons=fields.Integer('No. Personas en Estado de Incapacidad',tracking=True)  

    #informacion de transporte
    driver_license=fields.Boolean('Licencia de Conducir',tracking=True)
    license_type=fields.Selection([('A1', 'A1'),('A2', 'A2'),('B1', 'B1'),('B2','B2'),('B3','B3'),('C1', 'C1'),('C2','C2'),('C3','C3')],'Tipo de Licencia de Conducir',tracking=True)
    main_transport=fields.Selection([('BICICLETA', 'BICICLETA'),('CAMINANDO', 'CAMINANDO'),('CARRO', 'CARRO'),('MOTO','MOTO'),('PATINETA','PATINETA'),('TRANSPORTE COMPARTIDO', 'TRANSPORTE COMPARTIDO'),('TRANSPORTE PRIVADO(TAXI, UBER, BEAT)','TRANSPORTE PRIVADO(TAXI, UBER, BEAT)')],'Medio de transporte Principal',tracking=True)
    second_transport=fields.Selection([('BICICLETA', 'BICICLETA'),('CAMINANDO', 'CAMINANDO'),('CARRO', 'CARRO'),('MOTO','MOTO'),('PATINETA','PATINETA'),('TRANSPORTE COMPARTIDO', 'TRANSPORTE COMPARTIDO'),('TRANSPORTE PRIVADO(TAXI, UBER, BEAT)','TRANSPORTE PRIVADO(TAXI, UBER, BEAT)')],'Medio de transporte secundario',tracking=True)
    commute_hours=fields.Selection([('MENOS DE 30 MINUTOS', 'MENOS DE 30 MINUTOS'),('30 MINUTOS', '30 MINUTOS'),('1 HORA', '1 HORA'),('1.5 HORAS','1.5 HORAS'),('2 HORAS','2 HORAS'),('2.5 HORAS', '2.5 HORAS'),('3 HORAS','3 HORAS'),('3.5 HORAS','3.5 HORAS'),('4 HORAS','4 HORAS'),('4.5 HORAS','4.5 HORAS')],'Horas en llegar al trabajo',tracking=True)
    civil_state=fields.Selection([('SOLTERO/A', 'SOLTERO/A'),('CASADO/A', 'CASADO/A'),('DIVORCIADO/A', 'DIVORCIADO/A'),('UNIÓN LIBRE','UNIÓN LIBRE'),('VIUDO/A','VIUDO/A')],tracking=True)

    #campos conyugue
    first_surname_spouse=fields.Char(string="Primer Apellido del Cónyugue",tracking=True)
    second_surname_spouse=fields.Char(string="Segundo Apellido del Cónyugue",tracking=True)
    first_name_spouse=fields.Char(string="Primer Nombre del Cónyugue",tracking=True)
    second_name_spouse=fields.Char(string="Segundo Nombre del Cónyugue",tracking=True)
    education_spouse=fields.Selection([('Primaria', 'PRIMARIA'),('Bachiller', 'BACHILLER'),('Curso o Seminario', 'CURSO O SEMINARIO'),('Técnica','TÉCNICA'),('Tecnológica','TECNOLÓGICA'),('Universitaria', 'UNIVERSITARIA'),('Especialización', 'ESPECIALIZACIÓN'),('Maestría','MAESTRÍA'),('Doctorado','DOCTORADO')],tracking=True)
    gender_spouse=fields.Selection([('male', 'Masculino'),('female', 'Femenino'), ('other', 'Otro')])
    born_city_spouse=fields.Many2one('res.city')
    born_country_spouse = fields.Many2one('res.country')
    birthdate_spouse = fields.Date("Fecha nacimiento conyugue")

    #campos relacionados traidos de la requisición
    requisition_id=fields.Many2one('hr.requisition',tracking=True)
    req_company=fields.Char(string='Empresa', related='requisition_id.company_id.name',tracking=True)
    req_job=fields.Char(string="Cargo al que Aplica", related="requisition_id.job_id.name",tracking=True)
    req_immediate_boss=fields.Char(string="Jefe Inmediato", related="requisition_id.immediate_boss_id.name",tracking=True)
    req_sede=fields.Char(string="Sede", related="requisition_id.sede",tracking=True)
    req_area=fields.Char(string="Área", related="requisition_id.area")   
    req_work_shift_id=fields.Many2one(related="requisition_id.work_shift_id",tracking=True)
    req_in_charge_of_personnel=fields.Boolean(related="requisition_id.in_charge_of_personnel",tracking=True)
    req_therapist=fields.Many2one(related="requisition_id.req_therapist", string="Psicologo")
    req_recruiter=fields.Many2one(related="requisition_id.req_recruiter", string="Reclutador")
    req_city = fields.Many2one(related="requisition_id.city_id", string="Ciudad de requisición",tracking=True)
    #experiencia del aplicante
    resume_line_ids = fields.One2many('hr.resume.line', 'applicant_id', string="Resumé lines",tracking=True)
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills",tracking=True) 
    education_level=fields.Selection([('Primaria', 'PRIMARIA'),('Bachiller', 'BACHILLER'),('Curso o Seminario', 'CURSO O SEMINARIO'),('Técnica','TÉCNICA'),('Tecnológica','TECNOLÓGICA'),('Universitaria', 'UNIVERSITARIA'),('Especialización', 'ESPECIALIZACIÓN'),('Maestría','MAESTRÍA'),('Doctorado','DOCTORADO')],tracking=True)
    currently_studying=fields.Boolean()  
    #informacion especifica
    phobia_ids=fields.Many2many('hr.employee.phobia',tracking=True)
    hobby_ids=fields.Many2many('hr.employee.hobby',tracking=True)
    has_desease=fields.Char(string="Tiene alguna enfermedad Importante",tracking=True)
    take_medicine=fields.Char(string="Toma algun Medicamento",tracking=True)
    allergy_ids=fields.Many2many('hr.employee.allergy')
    #campos tipo adjuntos (documentos personales)
    identification_copy=fields.Binary(tracking=True, copy=False)
    identification_copy_filename = fields.Char("File Name")
    education_cert=fields.Binary(tracking=True)
    education_cert_emp_filename = fields.Char("File Name")
    laboral_cert=fields.Binary(tracking=True)
    laboral_cert_emp_filename = fields.Char("File Name") 
    cv=fields.Binary(tracking=True)
    cv_filename = fields.Char("File Name")
    condition_approval=fields.Binary(tracking=True)
    condition_approval_emp_filename = fields.Char("File Name")
    militar_document=fields.Binary(tracking=True)
    militar_document_emp_filename = fields.Char("File Name")
    personal_references=fields.Binary(tracking=True)
    personal_references_emp_filename = fields.Char("File Name")
    reference_verification=fields.Binary(tracking=True)
    reference_verification_emp_filename = fields.Char("File Name")     
    bank_account_cert=fields.Binary(tracking=True)
    bank_account_cert_emp_filename = fields.Char("File Name")
    disciplinary_background=fields.Binary(tracking=True)
    disciplinary_background_emp_filename = fields.Char("File Name")
    background_validation=fields.Binary(tracking=True)
    background_validation_emp_filename = fields.Char("File Name")
    immediate_boss_interview=fields.Binary(tracking=True)
    immediate_boss_interview_emp_filename = fields.Char("File Name")
    photographs=fields.Binary(tracking=True)
    photographs_emp_filename = fields.Char("File Name")
    sarlaft_validation=fields.Binary(tracking=True)
    sarlaft_validation_emp_filename = fields.Char("File Name")
    solidarity_tgs=fields.Binary(tracking=True)
    solidarity_tgs_filename = fields.Char("File Name") 
    soat = fields.Binary(tracking=True)
    soat_filename = fields.Char("File Name")   
    security_study=fields.Binary(tracking=True)
    security_study_emp_filename = fields.Char("File Name")
    medical_exams=fields.Binary(tracking=True)
    medical_exams_emp_filename = fields.Char("File Name")
    funeral_policy=fields.Binary(tracking=True)
    funeral_policy_emp_filename = fields.Char("File Name")
    email_usage_auth=fields.Binary(tracking=True)
    email_usage_auth_emp_filename = fields.Char("File Name")
    driver_license=fields.Binary(tracking=True)
    driver_license_emp_filename = fields.Char("File Name")
    vehicle_ownership=fields.Binary(tracking=True)
    vehicle_ownership_emp_filename = fields.Char("File Name")
    runt_cert=fields.Binary(tracking=True)
    runt_cert_emp_filename = fields.Char("File Name")
    revision_tecnico_mecanica=fields.Binary(tracking=True)
    revision_tecnico_mecanica_emp_filename = fields.Char("File Name")
    induction_center = fields.Binary(tracking=True)
    induction_center_emp_filename = fields.Char("File Name")
    sena_cert = fields.Binary(tracking=True)
    sena_certfile_name = fields.Char("File Name")

    #campos: pruebas
    apply_psychotechnical_test = fields.Boolean(tracking=True, string="Aplica prueba Técnica")
    apply_technical_test = fields.Boolean(tracking=True, string="Aplica prueba Psicotécnica")
    technical_test = fields.Binary(tracking=True)
    technical_test_filename = fields.Char("Adjunto prueba Técnica")
    psychotechnical_test = fields.Binary(tracking=True)
    psychotechnical_test_filename = fields.Char("Adjunto prueba Psicotécnica")
    soft_skill_ids = fields.Many2many('hr.skill', string='Habilidades Principales')
    technical_results = fields.One2many('hr.applicant.skill', 'applicant_id', string='Resultados Prueba Técnica')
    test_stage = fields.Boolean(related="stage_id.test_stage")
    test_required = fields.Boolean(compute="_compute_test_required")
    recruitment_stage_seq=fields.Integer(related="stage_id.sequence")
    #campos: Razón de la Excepción
    # hiring_exc_training=fields.Boolean(tracking=True)
    # hiring_exc_experience=fields.Boolean(tracking=True)
    # hiring_exc_skills=fields.Boolean(tracking=True)
    # hiring_exc_education=fields.Boolean(tracking=True)
    # exc_commitment_date=fields.Date(tracking=True)
    # exc_due_date=fields.Date(tracking=True)
    # exc_action_plan=fields.Text(tracking=True)
    requisition_name = fields.Char(related="requisition_id.name", string="Identificador de la Requisición")

    @api.constrains('stage_id')
    def _check_test_stage(self):
        for rec in self:
            test_stage_sequence = rec.stage_id.search([('test_stage', '=', True), ('active', '=', True)], order='sequence', limit=1).sequence
            if test_stage_sequence and rec.stage_id.sequence >= test_stage_sequence and rec.apply_psychotechnical_test and not rec.psychotechnical_test :
                raise ValidationError("Por favor adjuntar resultados de pruebas psicotécnicas")
            if test_stage_sequence and rec.stage_id.sequence >= test_stage_sequence and rec.apply_technical_test and not rec.technical_test:
                raise ValidationError("Por favor adjuntar resultados de pruebas técnicas")

    @api.depends('stage_id')
    def _compute_test_required(self):
        for rec in self:
            test_stage_sequence = rec.stage_id.search([('test_stage', '=', True), ('active', '=', True)], order='sequence', limit=1).sequence
            if test_stage_sequence and rec.stage_id.sequence >= test_stage_sequence:
                rec.test_required = True
            else: rec.test_required = False
            
             
    @api.onchange('from_date', 'final_date','total_days')
    def calculate_date(self):
        if self.from_date and self.final_date:
            d1=datetime.strptime(str(self.from_date),'%Y-%m-%d') 
            d2=datetime.strptime(str(self.final_date),'%Y-%m-%d')
            d3=d2-d1
            self.total_days=str(d3.days)      

    @api.constrains('nit')
    def _check_nit_size(self):
        pattern = "^\+?[0-9]*$" 
        for record in self:
            if record.nit and re.match(pattern, record.nit) is None:
                raise ValidationError(("NIT debe ser numerico"))

    @api.model
    def _concat_args(self, *argv):
        args = tuple(filter(lambda x: x, argv))
        return " ".join(map(str.upper, args))

    #concatenación Dirección tipo DIAN
    @api.onchange('addressm_id', 'main_road', 'generator_road', 'land', 'road_complement')                  
    def _onchange_direccion_dian(self):
        self.full_address = self._concat_args(
            self.addressm_id.identificador,
            self.main_road,
            self.generator_road,
            self.land,
            self.road_complement
        )

    #concatenación asunto/solicitante
    @api.onchange('requisition_name','req_job', 'partner_name')                  
    def _onchange_name(self):
        self.name = "[%s] %s / %s" % (
            self.requisition_name if self.requisition_name else "",
            self.req_job if self.req_job else "",          
            self.partner_name if self.partner_name else "")

    #concatenación: Nombre del aplicante
    @api.onchange('first_name', 'second_name', 'first_surname', 'second_surname')
    def _onchange_applicant_name(self):
        self.partner_name = self._concat_args(
            self.first_name,
            self.second_name,
            self.first_surname,
            self.second_surname
        )

    # validar numero de identifiacion y confirmacion del mismo. 
    @api.constrains('identification_id', 'confirm_id')
    def _check_id(self):
        for record in self:
            if record.identification_id != record.confirm_id:
                raise ValidationError("Verificar Número de Identificación : %s" % record.identification_id)

    #validar fecha de nacimiento
    @api.constrains('birth_date', 'confirm_birthdate')
    def _check_birth_date(self):
        for record in self:
            if record.birth_date != record.confirm_birthdate:
                raise ValidationError("Verificar fecha de nacimiento! : %s" % record.birth_date)
    
    #validar correo electronico
    @api.constrains('email_from', 'emal_cc')
    def _check_email(self):
        for record in self:
            if record.email_from != record.emal_cc:
                raise ValidationError("Verificar Correo! : %s" % record.email_from)

    def create_employee_from_applicant(self):
        res = super(HrApplicant, self).create_employee_from_applicant()
        if self.partner_id:
            address = self._concat_args(
                self.addressm_id.identificador,
                self.main_road,
                self.generator_road,
                self.land,
                self.road_complement,)
            self.partner_id.write({
                "vat": self.identification_id,
                "street": address,
                "state_id": self.state_id.id,
                "country_id": self.state_id.country_id.id,
                "city_id": self.city_id.id,
                "city": self.city_id.name,
                "l10n_latam_identification_type_id": self.l10n_latam_identification_type_id.id,
                # "title": self.treatment_id.id,
                "firstname": self.first_name,
                "othernames": self.second_name,
                "lastname":self.first_surname,
                "lastname2": self.second_surname,
                "co_street_1": self.addressm_id.identificador,
                "co_street_2": self.main_road,
                "co_street_3": self.generator_road,
                "co_street_4": self.land,
                "co_street_5": self.road_complement,
            })
        employee_id = self.env['hr.employee'].browse(res.get('res_id'))
        vals = {
            'default_addressm_id': self.addressm_id.id,
            'default_main_road': self.main_road,
            'default_generator_road': self.generator_road,
            'default_land': self.land,
            'default_road_complement': self.road_complement,            
            'default_pants_size': self.pants_size,
            'default_shirt_size': self.shirt_size,
            'default_coat_size': self.coat_size,
            'default_shoes_size': self.shoes_size,
            'default_l10n_latam_identification_type_id': self.l10n_latam_identification_type_id.id,
            'default_identification_id': self.identification_id,
            'default_blood_group': self.blood_group,
            'default_gender': self.gender,
            'default_property_type': self.property_type,
            'default_other_property_type': self.other_property_type,
            'default_house_type': self.house_type,
            'default_other_house_type': self.other_house_type,
            'default_house_zone': self.house_zone,
            'default_energy_service': self.energy_service,
            'default_sewerage_service': self.sewerage_service,
            'default_aqueduct_service': self.aqueduct_service,
            'default_gas_service': self.gas_service,
            'default_trash_service': self.trash_service,
            'default_ethnic_group': self.ethnic_group,
            'default_stratum': self.stratum,
            'default_driver_license': self.driver_license,
            'default_license_type': self.license_type,
            'default_main_transport': self.main_transport,
            'default_second_transport': self.second_transport,
            'default_commute_hours': self.commute_hours,
            'default_first_name': self.first_name,
            'default_second_name': self.second_name,
            'default_third_name':self.first_surname,
            'default_fourth_name': self.second_surname,
            'default_civil_state': self.civil_state,
            'default_declare_income': self.declare_income,
            'default_afp_partner_id': self.afp_partner_id.id,
            'default_afc_partner_id': self.afc_partner_id.id,
            'default_eps_partner_id': self.eps_partner_id.id,
            'default_first_surname_spouse': self.first_surname_spouse,
            'default_second_surname_spouse': self.second_surname_spouse,
            'default_first_name_spouse': self.first_name_spouse,
            'default_second_name_parent': self.second_name_spouse,
            'default_gender_spouse': self.gender_spouse,
            'default_has_dependents': self.has_dependents,
            'default_family_head': self.family_head,
            'default_family_size': self.family_size,
            'default_disability_persons': self.disability_persons,
            'default_contact_name': self.contact_name,
            'default_contact_phone': self.contact_phone,
            'default_relationship': self.relationship,
            'default_other_relationship': self.other_relationship,
            'default_contact_full_address': self.contact_full_address,
            'default_hobby_ids': self.hobby_ids.ids, 
            'default_phobia_ids': self.phobia_ids.ids, 
            'default_allergy_ids':self.allergy_ids.ids, 
            'default_requisition_id': self.requisition_id.id,
            'default_neighborhood': self.neighborhood,
            'default_has_desease': self.has_desease,
            'default_take_medicine': self.take_medicine,
            'default_city_residence': self.city_id.id,
            'default_state_id': self.state_id.id,
            'default_native_lang_id': self.native_lang_id.id,
            'default_pet_ids': self.pet_ids.ids, 
            'default_son_ids': self.son_ids.ids,         
            'default_telefono_del_empleado': self.partner_phone,
            'default_celular_del_empleado': self.partner_mobile,
            'default_correo_privado_del_empleado': self.email_from,
            'default_treatment_id': self.treatment_id.id,
            'default_expedition_city_id': self.expedition_city_id.id,
            'default_birthday': self.birth_date,
            'default_confirmation_date_of_birth': self.confirm_birthdate,
            'default_place_of_birth': self.place_of_birth,
            'default_country_of_birth': self.country_id.id,
            'default_born_country_spouse': self.born_country_spouse.id,
            'default_birthdate_spouse': self.birthdate_spouse,
            'default_education_level': self.education_level,
            'default_currently_studying': self.currently_studying,
            'default_lang_ids': self.lang_ids.ids, 
            'default_country_id': self.country_id.id,
            'default_education_spouse': self.education_spouse,
            'default_born_city_spouse': self.born_city_spouse.id,
            'default_education_ids': self.education_ids.ids, 
            'default_resume_line_ids': self.resume_line_ids.ids, 
            'default_identification_copy': self.identification_copy,
            'default_identification_copy_filename': self.identification_copy_filename, 
            'default_background_validation_emp': self.background_validation,
            'default_cv_emp': self.cv,
            'default_education_cert_emp': self.education_cert,
            'default_laboral_cert_emp': self.laboral_cert,
            'default_condition_approval_emp': self.condition_approval,
            'default_militar_document_emp': self.militar_document,
            'default_personal_references_emp': self.personal_references,
            'default_reference_verification_emp': self.reference_verification,
            'default_bank_account_cert_emp': self.bank_account_cert,
            'default_disciplinary_background_emp': self.disciplinary_background,
            'default_immediate_boss_interview_emp': self.immediate_boss_interview,
            'default_photographs_emp': self.photographs,
            'default_sarlaft_validation_emp': self.sarlaft_validation,
            'default_security_study_emp': self.security_study,
            'default_medical_exams_emp': self.medical_exams,
            'default_funeral_policy_emp': self.funeral_policy,
            'default_email_usage_auth_emp': self.email_usage_auth,
            'default_driver_license_emp': self.driver_license,
            'default_vehicle_ownership_emp': self.vehicle_ownership,
            'default_runt_cert_emp': self.runt_cert,
            'default_revision_tecnico_mecanica_emp': self.revision_tecnico_mecanica,
            'default_induction_center_emp': self.induction_center,
            'default_sena_cert_emp': self.sena_cert,
            'default_education_cert_emp_filename': self.education_cert_emp_filename,
            'default_laboral_cert_emp_filename': self.laboral_cert_emp_filename,
            'default_cv_emp_filename': self.cv_filename,
            'default_condition_approval_emp_filename': self.condition_approval_emp_filename,
            'default_militar_document_emp_filename': self.militar_document_emp_filename,
            'default_personal_references_emp_filename': self.personal_references_emp_filename,
            'default_reference_verification_emp_filename': self.reference_verification_emp_filename,
            'default_bank_account_cert_emp_filename': self.bank_account_cert_emp_filename,
            'default_disciplinary_background_emp_filename': self.disciplinary_background_emp_filename,
            'default_background_validation_emp_filename': self.background_validation_emp_filename,
            'default_immediate_boss_interview_emp_filename': self.immediate_boss_interview_emp_filename,
            'default_photographs_emp_filename': self.photographs_emp_filename,
            'default_sarlaft_validation_emp_filename': self.sarlaft_validation_emp_filename,           
            'default_security_study_emp_filename': self.security_study_emp_filename,
            'default_medical_exams_emp_filename': self.medical_exams_emp_filename,
            'default_funeral_policy_emp_filename': self.funeral_policy_emp_filename,
            'default_email_usage_auth_emp_filename': self.email_usage_auth_emp_filename,
            'default_driver_license_emp_filename': self.driver_license_emp_filename,
            'default_vehicle_ownership_emp_filename': self.vehicle_ownership_emp_filename,
            'default_runt_cert_emp_filename': self.runt_cert_emp_filename,
            'default_soat': self.soat,
            'default_soat_filename': self.soat_filename,
            'default_revision_tecnico_mecanica_emp_filename': self.revision_tecnico_mecanica_emp_filename,
            'default_induction_center_emp_filename': self.induction_center_emp_filename,
            'default_sena_certfile_name': self.sena_certfile_name,
            'default_solidarity_tgs': self.solidarity_tgs,
            'default_solidarity_tgs_filename': self.solidarity_tgs_filename,
            'default_technical_test': self.technical_test,
            'default_technical_test_filename': self.technical_test_filename,
            'default_psychotechnical_test': self.psychotechnical_test,
            'default_psychotechnical_test_filename': self.psychotechnical_test_filename,
            'default_applicant': self.partner_name,
            'default_full_address': self.full_address,
        }
        res["context"].update(vals)
        return res

    #funcion para traer campos de la requisicion editables    
    @api.onchange('requisition_id')
    def _onchange_requisition_id(self):
      if self.requisition_id:
         self.job_id = self.requisition_id.job_id.id

    
    @api.onchange('main_road','generator_road','land','road_complement')
    def _onchange_address(self):
        self.main_road = self.main_road.upper() if self.main_road else False
        self.generator_road = self.generator_road.upper() if self.generator_road else False
        self.land = self.land.upper() if self.land else False
        self.road_complement = self.road_complement.upper() if self.road_complement else False

    #funcion para colocar nombre del conyugue en mayusculas. 
    # @api.onchange('first_surname_spouse','first_surname_spouse','first_name_spouse','second_name_spouse')
    # def _compute_maj_solicitante(self):
    #     self.first_surname_spouse = self.first_surname_spouse.upper() if self.first_surname_spouse else False
    #     self.first_surname_spouse = self.first_surname_spouse.upper() if self.first_surname_spouse else False
    #     self.first_name_spouse = self.first_name_spouse.upper() if self.first_name_spouse else False
    #     self.second_name_spouse = self.second_name_spouse.upper() if self.second_name_spouse else False

class HrApplicantSkill(models.Model):
    _name = 'hr.applicant.skill'
    _description = "Skill level for an applicant"
    _rec_name = 'skill_id'

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    skill_id = fields.Many2one('hr.skill', required=True)
    result = fields.Float("Result")