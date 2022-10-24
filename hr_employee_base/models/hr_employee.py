# -*- coding: utf-8 -*-
from odoo import fields, models, api
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


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    #principal
    company_id= fields.Many2one('res.company',tracking=1)
    first_name= fields.Char('Primer Nombre',required=False,  tracking=2)
    second_name = fields.Char('Segundo Nombre',tracking=3)
    third_name = fields.Char('Primer Apellido',required=False,tracking=4)
    fourth_name = fields.Char('Segundo Apellido',tracking=5)
    requisition_id = fields.Many2one('hr.requisition','Requisiciones',tracking=6)
    applicant=fields.Char('Aplicante')
    requesting_employee = fields.Char(string='Solicitante',related='requisition_id.requesting_employee.name',tracking=7)
    req_city = fields.Many2one('res.city',string="Ciudad de Requisición",tracking=8)
    req_sede = fields.Char(string="Sede",tracking=9)
    req_area = fields.Char(string="Area",tracking=10)
    treatment = fields.Selection([('SR.','SR.'),('SRA.','SRA.')],'Tratamiento', tracking=11)
    treatment_id = fields.Many2one('res.partner.title', string='Tratamiento')
    organizational_unit_id = fields.Many2one('hr.employee.unit', tracking=12)
    cost_center_id = fields.Many2one('hr.employee.cost.center',string="Número del Centro de Costo",tracking=13)

    req_disability_handling_id = fields.Many2one("hr.disability.handling",string="Manejo de Incapacidades")
    agreement = fields.Selection([('PACTO COLECTIVO', 'PACTO COLECTIVO'),('CONVENCIÓN COLECTIVA DE TRABAJO', 'CONVENCIÓN COLECTIVA DE TRABAJO'),('NO APLICA','NO APLICA')],string="Pacto/Convención")
    #Private Information
    # applicant_id = fields.Many2one('hr.applicant')
    education_ids = fields.One2many('hr.employee.education','employee_id','Formación')

    #employee_id One2many
    lang_ids = fields.One2many('hr.employee.lang','employee_id','Idiomas')
    pet_ids = fields.One2many('hr.employee.pet','employee_id', 'Mascotas')
    son_ids = fields.One2many('hr.employee.son', 'employee_id', 'Hijos')
    asset_line_ids = fields.One2many('hr.job.asset', 'employee_id', 'Activos')
    #1 grupo
    confirmation_date_of_birth = fields.Date('Confirmacion Fecha de Nacimiento',tracking=14)
    state_id = fields.Many2one('res.country.state','Departamento',tracking=15)
    city_residence = fields.Many2one('res.city', 'Ciudad de Residencia',tracking=16)
    neighborhood = fields.Char('Barrio de residencia',tracking=17)
    # identification_type = fields.Many2one('l10n_latam.identification.type', string='Tipo de documento', tracking=18)
    l10n_latam_identification_type_id = fields.Many2one('l10n_latam.identification.type', string='Tipo de documento', tracking=18)
    expedition_city_id = fields.Many2one('res.city','Lugar de Expedición',tracking=19)
    country_of_birth = fields.Many2one('res.country','País de Nacimiento')
    #2 grupo
    pants_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')],'Talla Pantalon')
    shirt_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')],'Talla Camisa')
    coat_size = fields.Selection([('XS', 'XS'),('S', 'S'),('M', 'M'), ('L', 'L'),('XL','XL'),('XXL','XXL')],'Talla Saco')
    shoes_size = fields.Selection(tallazapatos,'Talla Zapatos')
    #3 grupo
    confirmation_email = fields.Char('Confirmación del correo')
    native_lang_id = fields.Many2one('res.lang','Idioma Nativo',tracking=20)
    blood_group = fields.Selection(grupo_san,'Grupo Sanguíneo',tracking=21)
    gender = fields.Selection([('male', 'Masculino'),('female', 'Femenino'), ('other', 'Otro')])
    declare_income = fields.Boolean('Declara usted renta?')
    #4 grupo dirección de residencia
    addressm_id = fields.Many2one('hr.employee.address','Vía principal',tracking=22)
    main_road = fields.Char('Nombre Vía Principal',tracking=23)
    generator_road = fields.Char('Via Generadora',tracking=24)
    land = fields.Char('Predio',tracking=25)
    road_complement = fields.Char('Complemento',tracking=26)
    full_address = fields.Char('Dirección Completa',tracking=27)
    #información de vivienda
    property_type = fields.Selection([
        ('rented', 'ARRENDADO'),
        ('community', 'COMUNITARIA'),
        ('family', 'FAMILIAR'),
        ('own', 'PROPIA'),
        ('other', 'OTRO')
    ],'Tipo de Vivienda')
    other_property_type = fields.Char('¿Cuál tipo de vivienda?')
    house_type = fields.Selection([('CASA', 'CASA'),('APARTAMENTO', 'APARTAMENTO'),('HABITACIÓN', 'HABITACIÓN'),('OTRO','OTRO')],'Caracteristicas de la Vivienda')
    other_house_type = fields.Char('¿Cúal Caracteristica de Vivienda?')
    house_zone = fields.Selection([('RURAL', 'RURAL'),('URBANA', 'URBANA'),('SUB', 'SUB URBANA')],'Zona de la Vivienda')
    energy_service = fields.Boolean('Cuenta con servicio de Energia eléctrica?')
    sewerage_service = fields.Boolean('Cuenta con servicio de alcantarillado?')
    aqueduct_service = fields.Boolean('Cuenta con servicio de acueducto?')
    #5 grupo
    gas_service = fields.Boolean('Cuenta con servicio de Gas Natural?')
    trash_service = fields.Boolean('Cuenta con servicio de Recolección de trash_service?')
    ethnic_group = fields.Selection([('Mestizo', 'MESTIZO'),('Blanco', 'BLANCO'),('Afrocolombiano', 'AFROCOLOMBIANO'),('Indigena','INDIGENA'),('Gitano','GITANO')],'Grupo Étnico')
    stratum = fields.Selection([('1', 'ESTRATO 1'),('2', 'ESTRATO 2'),('3', 'ESTRATO 3'),('4','ESTRATO 4'),('5','ESTRATO 5'),('6','ESTRATO 6')],'Estrato Socioeconómico',tracking=28)

    #6 grupo persona en caso de emergencia//
    contact_name = fields.Char('Nombre Completo',tracking=29)
    contact_phone = fields.Char('Telefono',tracking=30)
    relationship = fields.Selection([('grandparent', 'ABUELO (A)'),('friend', 'AMIGO (A)'),('spouse', 'ESPOSO (A)'),('sibling','HERMANO (A)'),('father','PADRE'),('mother','MADRE'),('nephew','SOBRINO (A)'),('uncle/aunt','TIO (A)'),('son/daughter','HIJO (A)'),('other','OTRO')],tracking=True)
    other_relationship = fields.Char('Otro parentesco',tracking=31)
    #dirección
    contact_address_id = fields.Many2one('hr.employee.address','Vía Principal')
    contact_main_road = fields.Char('Nombre Vía Principal')
    contact_generator_road = fields.Char('Via Generadora')
    contact_land = fields.Char('Predio')
    contact_road_complement = fields.Char('Complemento')
    contact_full_address = fields.Char('Dirección Completa',tracking=32)
    #7 grupo
    has_dependents = fields.Boolean('Tiene dependientes económicos?')
    family_head = fields.Boolean('Es cabeza de familia?')
    family_size = fields.Integer('Número de personas del núcleo familiar')
    disability_persons = fields.Integer('Número de personas en estado de discapacidad')

    #9 grupo
    driver_license = fields.Boolean('Tiene Licencia para conducir?')
    license_type = fields.Selection([('A1', 'A1'),('A2', 'A2'),('B1', 'B1'),('B2','B2'),('B3','B3'),('C1', 'C1'),('C2','C2'),('C3','C3')],'Tipo de Licencia')
    main_transport = fields.Selection([('BICICLETA', 'BICICLETA'),('CAMINANDO', 'CAMINANDO'),('CARRO', 'CARRO'),('MOTO','MOTO'),('PATINETA','PATINETA'),('TRANSPORTE COMPARTIDO', 'TRANSPORTE COMPARTIDO'),('TRANSPORTE PRIVADO(TAXI, UBER, BEAT)','TRANSPORTE PRIVADO(TAXI, UBER, BEAT)')],'Medio de Transporte Principal')
    second_transport = fields.Selection([('BICICLETA', 'BICICLETA'),('CAMINANDO', 'CAMINANDO'),('CARRO', 'CARRO'),('MOTO','MOTO'),('PATINETA','PATINETA'),('TRANSPORTE COMPARTIDO', 'TRANSPORTE COMPARTIDO'),('TRANSPORTE PRIVADO(TAXI, UBER, BEAT)','TRANSPORTE PRIVADO(TAXI, UBER, BEAT)')],'Medio de Transporte Secundario	')
    commute_hours = fields.Selection([('MENOS DE 30 MINUTOS', 'MENOS DE 30 MINUTOS'),('30 MINUTOS', '30 MINUTOS'),('1 HORA', '1 HORA'),('1.5 HORAS','1.5 HORAS'),('2 HORAS','2 HORAS'),('2.5 HORAS', '2.5 HORAS'),('3 HORAS','3 HORAS'),('3.5 HORAS','3.5 HORAS'),('4 HORAS','4 HORAS'),('4.5 HORAS','4.5 HORAS')],'Horas para llegar al trabajo')
    civil_state = fields.Selection([('SOLTERO/A', 'SOLTERO/A'),('CASADO/A', 'CASADO/A'),('DIVORCIADO/A', 'DIVORCIADO/A'),('UNIÓN LIBRE','UNIÓN LIBRE'),('VIUDO/A','VIUDO/A')],'Estado Civil')
    #10 grupo
    first_surname_spouse = fields.Char('Primer Apellido del Conyugue')
    second_surname_spouse = fields.Char('Segundo Apellido del Conyugue')
    first_name_spouse = fields.Char('Primer Nombre del Conyugue')
    second_name_parent = fields.Char('Segundo Nombre del Conyugue')
    gender_spouse = fields.Selection([('male', 'Masculino'),('female', 'Femenino'), ('other', 'Otro')],'Genero Cónyuge')
    education_spouse=fields.Selection([('Primaria', 'PRIMARIA'),('Bachiller', 'BACHILLER'),('Curso o Seminario', 'CURSO O SEMINARIO'),('Técnica','TÉCNICA'),('Tecnológica','TECNOLÓGICA'),('Universitaria', 'UNIVERSITARIA'),('Especialización', 'ESPECIALIZACIÓN'),('Maestría','MAESTRÍA'),('Doctorado','DOCTORADO')],string="Escolaridad del Conyugue",tracking=True)
    born_city_spouse = fields.Many2one('res.city','Lugar de Nacimiento Cónyuge')
    born_country_spouse = fields.Many2one('res.country','País de Nacimiento Cónyuge')
    birthdate_spouse = fields.Date('Fecha de Nacimiento Cónyuge')
    #escolaridad del candidato/empleado
    education_level=fields.Selection([('Primaria', 'PRIMARIA'),('Bachiller', 'BACHILLER'),('Curso o Seminario', 'CURSO O SEMINARIO'),('Técnica','TÉCNICA'),('Tecnológica','TECNOLÓGICA'),('Universitaria', 'UNIVERSITARIA'),('Especialización', 'ESPECIALIZACIÓN'),('Maestría','MAESTRÍA'),('Doctorado','DOCTORADO')],'Escolaridad del Solicitante',tracking=True)
    currently_studying=fields.Boolean('Estudia Actualmente')
    resume_line_ids = fields.One2many('hr.resume.line', 'employee_id', string="Resumé lines")
    employee_skill_ids = fields.One2many('hr.employee.skill', 'employee_id', string="Skills")
    phobia_ids=fields.Many2many('hr.employee.phobia')
    hobby_ids=fields.Many2many('hr.employee.hobby',string="Hobbies")
    has_desease=fields.Char(string="Tiene alguna enfermedad Importante")
    take_medicine=fields.Char(string="Toma algun Medicamento")
    allergy_ids=fields.Many2many('hr.employee.allergy', string="Tiene alguna alergía?")
    #campos: entidades del sistema de seguridad
    eps_partner_id=fields.Many2one('res.partner','EPS')
    afp_partner_id=fields.Many2one('res.partner','AFP')
    afc_partner_id=fields.Many2one('res.partner','AFC')
    arl_partner_id=fields.Many2one('res.partner','ARL')
    ccf_partner_id=fields.Many2one('res.partner','Caja de Compensación')
    risk_type_id = fields.Many2one('hr.risk.type', string='Nivel de Riesgo')
    arl_risk=fields.Char(related="risk_type_id.code")
    # arl_risk=fields.Selection([('1 RIESGO I', '1 RIESGO I'),('2 RIESGO II', '2 RIESGO II'),('3 RIESGO III','3 RIESGO III'),('4 RIESGO IV','4 RIESGO IV'),('5 RIESGO V','5 RIESGO V')])
    benefit_type_id=fields.Many2one('hr.employee.benefit',string="Clase Beneficio")
    payrollcc_id=fields.Many2one('hr.employee.payrollcc',string="ccnómina")
    receptor_key_id=fields.Many2one('hr.employee.receptor.key',string="Clave Receptor")
    benefit_type_value=fields.Float(string="Importe Clase Beneficio")
    plan_exequial=fields.Selection([('Coopserfun', 'Coopserfun'),('Coorserpark', 'Coorserpark'),('La Ascención','La Ascención'),('Los Olivos','Los Olivos'),('Recordar S.A.','Recordar S.A.')])
    funeral_plan_value=fields.Integer(string="Importe Plan Exequial")
    contributor_type_id=fields.Many2one('hr.employee.contributor.type',string="Tipo de Cotizante")
    contributor_subtype_id=fields.Many2one('hr.employee.contributor.subtype',string="Subtipo de Cotizante")
    loss_reason=fields.Selection([('1-VACANTE', '1-VACANTE'),('2-Aumento de la Planta', '2-AUMENTO DE LA PLANTA'),('3-Creación del Cargo', '3-CREACIÓN DEL CARGO'), ('4-Reemplazo', '4-REEMPLAZO')],default='1-VACANTE',string="Motivo de Pérdida")
    salary_type_id=fields.Many2one('hr.employee.salary.type',string="Tipo de Salario")
    posicion_emp=fields.Char(string="Posición")
    area_nivel_cargo_emp=fields.Selection([('1-GRADO I', '1-GRADO I'),('2-GRADO II', '2-GRADO II'),('3-GRADO III', '3-GRADO III'), ('4-GRADO IV', '4-GRADO IV'),('ZZ-PENSIONADO','ZZ-PENSIONADO')],string="Area Nivel Cargo")
    grupo_sueldos_emp=fields.Selection([('13', '13'),('14', '14')],string="Grupo de Sueldos")
    grado_ocupacion_emp=fields.Selection([('13', '13'),('14', '14')],string="Grado de Ocupación")
    hora_trabajo_periodo_emp=fields.Selection([('120', '120'),('240', '240')],string="Horas de Trabajo Periodo")
    procedimiento_emp=fields.Integer(default=1, string="Procedimiento")
    division_id=fields.Many2one('hr.employee.division', string="División")
    grupo_seleccion_emp=fields.Selection([('1 ACTIVOS', '1 ACTIVOS'),('2 PENSIONADOS', '2 PENSIONADOS'),('3 JUBILADO ANTICIPADO','3 JUBILADO ANTICIPADO'),('4 APRENDICES','4 APRENDICES'),('5 RETIRADOS','5 RETIRADOS'),('7 TEMPORALES','7 TEMPORALES'),('9 EXTERNOS','9 EXTERNOS')], string="Grupo de Selección")
    personal_area_id=fields.Many2one('hr.employee.area', string="Area Personal")
    relacion_laboral_emp=fields.Selection([('01 LEY 50', '01 LEY 50'),('02 RÉG.ANTERIOR', '02 RÉG.ANTERIOR'),('03 INTEGRAL','03 INTEGRAL'),('04 APRENDIZAJE','04 APRENDIZAJE'),('05 PENSIONADO','05 PENSIONADO'),('06 EXTERNO/TEMPOR','06 EXTERNO/TEMPOR')],string="Relación Laboral ")
    # evaluacion_tiempo_pht_emp=fields.Selection([('1- EVALUACIÓN DE TIEMPOS, REAL', '1- EVALUACIÓN DE TIEMPOS, REAL'),('2- EVALUACIÓN DE TIEMPOS, CDP', '2- EVALUACIÓN DE TIEMPOS, CDP'),('7- EVALUACIÓN DE TIEMPO SIN INTEGRACIÓN CÁLCULO DE NÓMINA','7- EVALUACION DE TIEMPO SIN INTEGRACIÓN CÁLCULO DE NÓMINA'),('8- SERVICIOS EXTERNOS','8- SERVICIOS EXTERNOS'),('9- EVALUACIÓN DE TIEMPOS TEÓRICOS','9- EVALUACIÓN DE TIEMPOS TEÓRICOS'),('0- SIN EVALUACIÓN DE TIEMPOS','0- SIN EVALUACIÓN DE TIEMPOS')],string="Evaluación de Tiempos PHT")
    turno_trabajo_emp=fields.Selection([('NORM', 'NORM'),('NORMLS', 'NORMLS')], string="Turno de Trabajo")
    time_eval_id=fields.Many2one('hr.employee.time_eval', string="Evaluación Tiempos")
    #foto14 grupo documentos_certificados
    identification_copy = fields.Binary(string="Fotocopia de la Cédula")
    identification_copy_filename = fields.Char("Adjunto Fotocopia de la Cédula")
    education_cert_emp = fields.Binary(string="Certificado de Estudio")
    education_cert_emp_filename = fields.Char("Adjunto Certificado de Estudio")
    laboral_cert_emp= fields.Binary(string="Certificaciones Laborales")
    laboral_cert_emp_filename = fields.Char("Adjunto Certificaciones Laborales")
    cv_emp = fields.Binary(string="Hoja de Vida")
    cv_emp_filename = fields.Char("Adjunto Hoja de Vida")
    #15 grupo documentos_personales
    condition_approval_emp = fields.Binary(string="Aceptación de Condiciones")
    condition_approval_emp_filename = fields.Char("Adjunto Aceptación de Condiciones")
    militar_document_emp = fields.Binary(string="Libreta Militar")
    militar_document_emp_filename = fields.Char("Adjunto Libreta Militar")
    personal_references_emp = fields.Binary(string="Referencias Personales")
    personal_references_emp_filename = fields.Char("Adjunto Referencias Personales")
    reference_verification_emp = fields.Binary(string="Verificación de Referencias")
    reference_verification_emp_filename = fields.Char("Adjunto Verificación de Referencias")
    bank_account_cert_emp = fields.Binary(string="Certificado de Cuenta Bancaría")
    bank_account_cert_emp_filename = fields.Char("Adjunto Certificado de Cuenta Bancaría")
    disciplinary_background_emp = fields.Binary(string="Antecedentes Disciplinarios")
    disciplinary_background_emp_filename = fields.Char("Adjunto Antecedentes Disciplinarios")
    background_validation_emp = fields.Binary(string="Validación de Antecedentes")
    background_validation_emp_filename = fields.Char("Adjunto Validación de Antecedentes")
    #informacion de datos personales
    telefono_del_empleado=fields.Char('Télefono')
    celular_del_empleado=fields.Char('Celular')
    correo_privado_del_empleado=fields.Char('Correo Privado')
    #16 grupo
    immediate_boss_interview_emp = fields.Binary(string="Entrevista Jefe Inmediato")
    immediate_boss_interview_emp_filename = fields.Char("Adjunto Entrevista Jefe Inmediato")
    photographs_emp = fields.Binary(string="Fotografías")
    photographs_emp_filename = fields.Char("Adjunto Fotografías")
    sarlaft_validation_emp = fields.Binary(string="Validación Sarlaft")
    sarlaft_validation_emp_filename = fields.Char("Adjunto Validación Sarlaft")
    solidarity_tgs=fields.Binary(string="TGS Solidarios")
    solidarity_tgs_filename = fields.Char("Adjunto TGS Solidarios")
    security_study_emp = fields.Binary(string="Estudio de Seguridad")
    security_study_emp_filename = fields.Char("Adjunto Estudio de Seguridad")
    medical_exams_emp = fields.Binary(string="Examenes Medicos")
    medical_exams_emp_filename = fields.Char("Adjunto Examenes Medicos")
    funeral_policy_emp = fields.Binary(string="Poliza")
    funeral_policy_emp_filename = fields.Char("Adjunto de Poliza")
    email_usage_auth_emp = fields.Binary(string="Autorización del Uso de Correo")
    email_usage_auth_emp_filename = fields.Char("Adjunto Autorización del Uso de Correo")
    driver_license_emp = fields.Binary(string="Licencia de Conducir")
    driver_license_emp_filename = fields.Char("Adjunto Licencia de Conducir")
    vehicle_ownership_emp = fields.Binary(string="Carta de Propiedad del Vehiculo")
    vehicle_ownership_emp_filename = fields.Char("Adjunto Carta de Propiedad del Vehiculo")
    runt_cert_emp = fields.Binary(string="Certificado RUNT")
    runt_cert_emp_filename = fields.Char("Adjunto Certificado RUNT")
    soat = fields.Binary(string="Seguro Obligatorio Vigente")
    soat_filename = fields.Char("Adjunto Seguro Obligatorio Vigente")
    revision_tecnico_mecanica_emp = fields.Binary(string="Revisión Técnico Mecanica")
    revision_tecnico_mecanica_emp_filename = fields.Char("Adjunto Revisión Técnico Mecanica")
    induction_center_emp = fields.Binary(string="Centro de Inducción")
    induction_center_emp_filename = fields.Char("Adjunto Centro de Inducción")
    sena_cert_emp = fields.Binary(string="Certificación Sena")
    documentos_generales = fields.Binary(string="Documentos Generales")
    documentos_generales_filename = fields.Char("Adjunto Documentos Generales")
    rut = fields.Binary('RUT')
    sena_certfile_name = fields.Char("Adjunto Certificación Sena")
    technical_test = fields.Binary()
    technical_test_filename = fields.Char("Adjunto prueba Técnica")
    psychotechnical_test = fields.Binary()
    psychotechnical_test_filename = fields.Char("Adjunto prueba Psicotécnica")
    #aprobaciones
    aprobador_ninel2 = fields.Boolean('Aprobador Nivel 2')
    aprobador_ninel3 = fields.Boolean('Aprobador Nivel 3')
    #fecha de retiro
    fecha_retiro = fields.Date(string="Fecha de Retiro", tracking=33)
    check = fields.Boolean(string="Retiro")
    check_tag_ids = fields.Boolean(compute='_compute_check_tag_ids', invisible=True)

    @api.model
    def _concat_args(self, *argv):
        args = tuple(filter(lambda x: x, argv))
        return " ".join(map(str.upper, args))


    @api.onchange('requisition_id')
    def action_req(self):
      for record in self:
        if record.requisition_id:
            record.req_area = record.requisition_id.area
            record.req_sede = record.requisition_id.sede
            record.req_city = record.requisition_id.city_id.id
            record.organizational_unit_id = record.requisition_id.organizational_unit_id.id
            record.cost_center_id = record.requisition_id.cost_center_id.id
            record.parent_id = record.requisition_id.immediate_boss_id.id
            record.job_id = record.requisition_id.job_id.id
            record.agreement = record.requisition_id.agreement
            record.req_disability_handling_id = record.requisition_id.disability_handling_id.id

    @api.depends('category_ids')
    def _compute_check_tag_ids(self):
        for record in self:
            record.check_tag_ids = True if record.category_ids and record.category_ids[0].name == 'APRENDIZ' else False    

    # concatenar nombre completo del empleado
    @api.onchange('treatment_id', 'name', 'first_name', 'second_name', 'third_name', 'fourth_name')
    def _onchange_names(self):
        self.first_name = self.first_name.upper() if self.first_name else False
        self.second_name = self.second_name.upper() if self.second_name else False
        self.third_name = self.third_name.upper() if self.third_name else False
        self.fourth_name = self.fourth_name.upper() if self.fourth_name else False
        self.name = self._concat_args(
            self.treatment_id.name,
            self.first_name,
            self.second_name,
            self.third_name,
            self.fourth_name
        )

    # validar fecha de nacimiento
    @api.constrains('birthday', 'confirmation_date_of_birth')
    def _check_birthday(self):
        for record in self:
            if record.birthday != record.confirmation_date_of_birth:
                raise ValidationError(
                    "Verificar la confirmación de su fecha de nacimiento! : %s" % record.confirmation_date_of_birth)

    @api.onchange('addressm_id', 'main_road','generator_road','land','road_complement')
    def _onchange_addresses(self):        
        self.main_road = self.main_road.upper() if self.main_road else False
        self.generator_road = self.generator_road.upper() if self.generator_road else False
        self.land = self.land.upper() if self.land else False
        self.road_complement = self.road_complement.upper() if self.road_complement else False
        self.full_address = self._concat_args(
            self.addressm_id.identificador,
            self.main_road,
            self.generator_road,
            self.land,
            self.road_complement
        )

    # @api.model
    # def create(self, vals):
    #     res = super(HrEmployee, self).create(vals)
    #     self.env['ir.attachment'].search([
    #         ('res_model', '=', "hr.employee"),
    #         ('res_field', '!=', False),
    #         ('res_id', 'in', res.id),
    #         ('name', 'not ilike', 'image'), 
    #         ('name', 'not ilike', 'avatar'),
    #     ]).write({"res_field":False})
    #     return res

    # def write(self, vals):
    #     res = super(HrEmployee, self).write(vals)
    #     for record in self:
    #         # campo binary crea un attachmente a menos que atributo attachment=False
    #         # no es necesario crear attachments nuevos, solo dejar el campo res_field vacio para que aparezca en el chatter
    #         self.self.env['ir.attachment'].search([
    #             ('res_model', '=', "hr.employee"),
    #             ('res_field', '!=', False),
    #             ('res_id', 'in', record.id),
    #             ('name', 'not ilike', 'image'), 
    #             ('name', 'not ilike', 'avatar'),
    #         ]).write({"res_field":False})
    #     return res
