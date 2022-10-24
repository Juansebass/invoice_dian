# -*- coding: utf-8 -*-



from odoo import fields, models


class HrContract(models.Model):
    """Hr Contract."""

    _inherit = 'hr.contract'

    recruitment_reason_id = fields.Many2one(
        'hr.recruitment.reason',
        'Recruitment Reasons', copy=False)
    create_absence = fields.Boolean(string='Create Absence', compute='_compute_create_absence_contract')

    def _compute_create_absence_contract(self):
        for record in self:
            if record.salary_type in ['APOYO SOSTENIMIENTO', 'apoyo_sostenimiento']:
                record.create_absence = False
            else:
                record.create_absence = True


class HrContractFlexWage(models.Model):
    _inherit = 'hr.contract.flex_wage'

    pv_id = fields.Many2one('hr.pv')
