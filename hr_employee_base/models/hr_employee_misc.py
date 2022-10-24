# -*- coding: utf-8 -*-
from odoo import fields,models


class HrEmployeeCostCenter(models.Model):
    _name = 'hr.employee.cost.center'
    _description = 'Employee Cost Center'

    name=fields.Char('Centro de costo')
    number=fields.Char()
    company_id=fields.Many2one('res.company')

class HrEmployeeUnit(models.Model):
    _name = 'hr.employee.unit'
    _description = 'Employee organizational unit'

    name = fields.Char('Unidad Organizativa')
    company_id=fields.Many2one('res.company')

class  HrEmployeeArea(models.Model):
    _name = 'hr.employee.area'
    _description = 'Employee Area'

    name=fields.Char('Área Personal')
    identifier=fields.Char('Identificador')

class HrEmployeeDivision(models.Model):
    _name = 'hr.employee.division'
    _description = 'Employee Division'
    name=fields.Char()
    identifier=fields.Char('Identificador')


class HrEmployeeBenefit(models.Model):
    _name = 'hr.employee.benefit'
    _description = 'Employee Benefit Type'
   
    name=fields.Char("Beneficio")
    identifier=fields.Char('Identificador')

class HrEmployeePayrollCc(models.Model):
    _name = 'hr.employee.payrollcc'
    _description =' Payroll CC'

    name=fields.Char()
    identifier=fields.Char('Identificador')


class HrEmployeeSalaryType(models.Model):
    _name = 'hr.employee.salary.type'
    _description = 'Employee salary type'

    name=fields.Char()

class HrEmployeeReceptorKey(models.Model):
    _name = 'hr.employee.receptor.key'
    _description = "Reveptor Key"

    name=fields.Char()
    identifier=fields.Char('Identificador')

class HrEmployeeAddress(models.Model):
    _name = 'hr.employee.address'
    _description = "Hr employee address"
    
    name=fields.Char()
    identificador = fields.Char('Identificador')

class HrEmployeeTimeEval(models.Model):
    _name = 'hr.employee.time_eval'
    _description = "Hr employee time evaluation"

    name=fields.Char()

class HrEmployeeAllergy(models.Model):
    _name = 'hr.employee.allergy'
    _description = 'Employee Allergies'

    name=fields.Char('Alergía')

class HrEmployeePhobia(models.Model):
    _name = 'hr.employee.phobia'
    _description = 'Employee phobias'

    name = fields.Char('Fobia')

class HrEmployeeHobby(models.Model):
    _name = 'hr.employee.hobby'
    _description = 'Employee Hobbies'

    name=fields.Char('Hobby')

class HrEmployeeLang(models.Model):
    _name = 'hr.employee.lang'
    _description = 'Employee Languages'

    name=fields.Char('Lenguaje')
    domain_percentage=fields.Integer(string="Porcentaje de Dominio")
    po=fields.Integer(related="domain_percentage")
    applicant_id = fields.Many2one('hr.applicant', 'Aplicante')
    employee_id = fields.Many2one('hr.employee', 'Empleado')


class HrEmployeePet(models.Model):
    _name = 'hr.employee.pet'
    _rec_name = 'pet_type'
    _description = 'Employee Pets'

    applicant_id = fields.Many2one('hr.applicant', 'Aplicante')
    employee_id = fields.Many2one('hr.employee', 'Empleado')    
    pet_type=fields.Selection([('birds', 'AVES'),('rabbits', 'CONEJOS'),('cats','GATOS'),('hamsters','HAMSTER'),('fish','PECES'),('dogs','PERROS'),('reptiles','REPTILES'),('other','OTROS')])   
    number_of_pets=fields.Integer('Número de Mascotas')

class HrEmployeeContributorType(models.Model):
    _name = 'hr.employee.contributor.type'
    _description = 'Employee contributor type'

    name=fields.Char('Tipo de cotizante')

class HrEmployeeContributorSubType(models.Model):
    _name = 'hr.employee.contributor.subtype'
    _description = 'Employee contributor subtype'

    name=fields.Char('Subtipo de Cotizante')

class HrEmployeeShiftType(models.Model):
    _name = 'hr.employee.shift.type'
    _description = 'Employee shift type'

    name=fields.Char('Turno')

class HrDisabilityHandling(models.Model):
    _name = 'hr.disability.handling'
    _description = 'Disability Handling'

    name=fields.Char('Manejo Incapacidades')

class HrJobType(models.Model):
    _name = 'hr.job.type'
    _description = 'Job type'

    name=fields.Char('Tipo Cargo')    

class HrRiskType(models.Model):
    _name = "hr.risk.type"
    _rec_name = "code"
    _description = 'Arl Risk'

    code = fields.Char('Código')
    name = fields.Char('Nombre')
    percentage = fields.Float('Porcentaje (%)', digits=(32, 6))

class ResRelationship(models.Model):
    _name = 'res.relationship'
    _description = 'Relationship with contact'

    name = fields.Char('Relationship')
