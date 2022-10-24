# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class HrJob(models.Model):
    _inherit = 'hr.job'

    hr_contract_alert_id = fields.Many2one(
        'hr.contract.alert', 'Contract Alert')
