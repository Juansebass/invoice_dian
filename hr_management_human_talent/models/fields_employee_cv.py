from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    req_city = fields.Many2one('res.city', 'City')
    organizational_unit_id = fields.Many2one('hr.employee.unit', 'Organization Unit')
    arl_partner_id = fields.Many2one('res.partner')
    arl_risk = fields.Selection(
        selection=[('1 RIESGO I', '1 RIESGO I'), ('2 RIESGO II', '2 RIESGO II'), ('3 RIESGO III', '3 RIESGO III'),
                   ('4 RIESGO IV', '4 RIESGO IV'), ('5 RIESGO V', '5 RIESGO V')])


class HrContract(models.Model):
    _inherit = 'hr.contract'

    req_city = fields.Many2one('res.city', 'City')
    trainee_type = fields.Selection(
        selection=[('ETAPA LECTIVA', 'ETAPA LECTIVA'), ('ETAPA PRODUCTIVA', 'ETAPA PRODUCTIVA'),
                   ('PRACTICANTE', 'PRACTICANTE UNIVERSITARIO')], string='Apprentice type')
    teaching_stage_end_date = fields.Date('Fecha fin etapa lectiva')
    productive_stage_start_date = fields.Date('Fecha inicio etapa productiva')
    productive_stage_end_date = fields.Date('Fecha inicio etapa productiva')
