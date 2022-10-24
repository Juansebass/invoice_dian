
# -*- coding: utf-8 -*-
from odoo import fields,models


class HrRecruitmentReason(models.Model):
    _inherit = 'hr.recruitment.reason'

    requisition_reason = fields.Boolean('Motivo de Requisición', default=True)

