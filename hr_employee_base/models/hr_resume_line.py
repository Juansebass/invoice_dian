# -*- coding: utf-8 -*-
from odoo import fields, models, api


class HrResumeLine(models.Model):
    _inherit = 'hr.resume.line'

    resume_line_job_sector= fields.Selection([('public', 'PÚBLICA'), ('private', 'PRIVADA')])
    resume_line_job_id = fields.Many2one('hr.resume.line.job')
    # contract_type = fields.Selection(
    #     [('fixed_therm', 'CONTRATO FIJO'), ('permanent', 'CONTRATO INDEFINIDO'),
    #      ('independent', 'INDEPENDIENTE'), ('freelance', 'OBRA Y LABOR'),
    #      ('service', 'PRESTACIÓN DE SERVICIOS')])
    contract_type_id = fields.Many2one('hr.contract.type', string='Tipo de Contrato')
    country_id = fields.Many2one('res.country')
    currently_working = fields.Boolean()
    applicant_id = fields.Many2one('hr.applicant', 'Aplicante')
    employee_id = fields.Many2one(required=False)
    total_days=fields.Integer(string="TOTAL DAYS")

    @api.onchange('date_start', 'date_end','total_days')
    def _onchange_total_days(self):
        if self.date_start and self.date_end:
            self.total_days = (self.date_end - self.date_start).days

class HrResumeLineJob(models.Model):
    _name = 'hr.resume.line.job'
    _description = 'Performed Job'

    name=fields.Char()