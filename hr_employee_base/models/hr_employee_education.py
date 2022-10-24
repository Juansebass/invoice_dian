# -*- coding: utf-8 -*-
from odoo import fields,models,api


class HrEmployeeEducation(models.Model):
    _name = 'hr.employee.education'
    _rec_name = 'title'
    _description = 'Employee Education Background'

    #one2many
    applicant_id = fields.Many2one('hr.applicant', 'Aplicante', tracking=True)
    employee_id = fields.Many2one('hr.employee', 'Empleado', tracking=True)

    education=fields.Selection([('elementary', 'PRIMARIA'),('high_school', 'BACHILLER'),('course', 'CURSO O SEMINARIO'),('technique','TÉCNICA'),('technology','TECNOLÓGICA'),('university', 'UNIVERSITARIA'),('specialization', 'ESPECIALIZACIÓN'),('master','MAESTRÍA'),('doctorate','DOCTORADO')])
    in_progress=fields.Boolean()
    institute=fields.Char(tracking=True)
    title=fields.Many2one('hr.employee.education.title', tracking=True)
    study_type=fields.Selection([('cert', 'FORMAL(CON CERTIFICADO)'),('no_cert', 'INFORMAL(SIN CERTIFICADO)')])
    state=fields.Selection([('postponed', 'APLAZADO'),('complete', 'COMPLETADO'),('incomplete','INCOMPLETO'),('other','OTRO')])
    country_id=fields.Many2one('res.country', tracking=True)
    duration=fields.Integer(tracking=True)
    duration_unit=fields.Selection([('years', 'AÑOS'),('classes', 'CLASES'),('days','DÍAS'),('months','MESES'),('weeks','SEMANAS'),('semesters','SEMESTRES')])
    grad_date=fields.Date(tracking=True)

class HrEmployeeStudyTitle(models.Model):
    _name = 'hr.employee.education.title'
    _description = 'Employee Education Title'

    name=fields.Char()
    












