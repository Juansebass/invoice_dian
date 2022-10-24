# -*- coding: utf-8 -*-
from odoo import fields,models,api


class HrEmployeeSon(models.Model):
    _name = 'hr.employee.son'
    _description = 'Employee sons/daughters'
    #One2many
    applicant_id = fields.Many2one('hr.applicant', 'Aplicante')
    employee_id = fields.Many2one('hr.employee', 'Empleado')
    
    #campos hijos
    name = fields.Char()
    first_surname = fields.Char()
    second_surname = fields.Char()
    second_name = fields.Char()
    birth_date = fields.Date()
    gender = fields.Selection([('male', 'Masculino'),('female', 'Femenino'), ('other', 'Otro')])
    blood_group = fields.Selection([
        ('A+', 'A+'),('A-', 'A-'),
        ('B+', 'B+'),('B-', 'B-'),
        ('AB+', 'AB+'),('AB-', 'AB-'),
        ('O+', 'O+'),('O-', 'O-')   
    ])
    nacionality = fields.Many2one('res.country')
    birth_country_id = fields.Many2one('res.country')
    id_document = fields.Char("Identificación")
    is_stepson = fields.Boolean("Hijastro")
    occupation = fields.Selection([('employee', 'EMPLEADO'),('student', 'ESTUDIANTE'),('unoccupied','DESOCUPADO')])
    education = fields.Selection([('elementary', 'PRIMARIA'),('high_school', 'BACHILLER'),('course','CURSO O SEMINARIO'),('technical','TÉCNICA'),('technology','TÉCNOLOGICA'),('university','UNIVERSITARIA'),('specialization','ESPECIALIZACIÓN'),('master','MAESTRÍA'),('doctorate','DOCTORADO')])