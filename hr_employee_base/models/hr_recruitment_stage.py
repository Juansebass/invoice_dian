
# -*- coding: utf-8 -*-
from odoo import fields,models


class HrRecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    active = fields.Boolean('active', default=True)
    test_stage = fields.Boolean('Etapa de pruebas')

