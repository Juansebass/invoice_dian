# -*- coding: utf-8 -*-
from odoo import fields,models


class HrJobAsset(models.Model):
    _name = 'hr.job.asset'
    _description = "Job assets"

    name=fields.Char()
    category = fields.Selection([('physical', 'FISICO'),('information', 'INFORMACIÓN'),('tech','TECNOLÓGICO'),('na','NO APLICA')])
    employee_id = fields.Many2one('hr.employee', 'Empleado')
    job_id = fields.Many2one('hr.job', 'Activos')
    job_name = fields.Char(related="job_id.name")
   
    
    