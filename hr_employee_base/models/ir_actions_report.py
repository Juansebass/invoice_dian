# -*- coding: utf-8 -*-
from odoo import fields, models


class IrActionsReport(models.Model):   
    _inherit = 'ir.actions.report'

    job_id = fields.Many2one('hr.job', 'Puesto de Trabajo')
    reporte = fields.Many2one('ir.actions.report', string="Informes")
    company_id = fields.Many2many('res.company', string="Compañía")
    
    