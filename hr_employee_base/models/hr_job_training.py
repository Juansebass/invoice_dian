# -*- coding: utf-8 -*-
from odoo import fields,models,api


class HrJobTraining(models.Model):
    _name = 'hr.job.training'
    _description = "Job training"
    
    job_id = fields.Many2one('hr.job', 'Formación', tracking=True)
    name=fields.Char(tracking=True)
    academic_cert=fields.Boolean(tracking=True)
    technical_test=fields.Boolean(tracking=True)
    job_cert=fields.Boolean(tracking=True)  
    
   