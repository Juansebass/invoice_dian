# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, datetime, date


class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.model
    def _default_contract_is_sena(self):
        for contract in self:
            if contract.job_id.monetization_sena_id.id:
                return True
        return False

    type_apprentice_sena = fields.Selection(string='Type of Apprentice', selection=[('lective', 'Lective Stage'), (
        'productive', 'Productive Stage')], required=False, tracking=True)
    start_date_lective_sena = fields.Date(string='Start Date Lective Stage', required=False, tracking=True)
    finish_date_lective_sena = fields.Date(string='Finish Date Lective Stage', required=False, tracking=True)
    start_date_productive_sena = fields.Date(string='Start Date Productive Stage', required=False, tracking=True)
    finish_date_productive_sena = fields.Date(string='Finish Date Productive Stage', required=False, tracking=True)
    contract_is_sena = fields.Boolean(string='Contract is Sena', default="_default_contract_is_sena", tracking=True)
    state_contract_sena = fields.Selection(string='State Contract Sena',
                                           selection=[('running', 'Running'), ('to_finalize', 'To Finalize'),
                                                      ('finalized', 'Finalized')],
                                           required=False, default='running', tracking=True)
    days_to_finalized = fields.Integer(string='Days to Finalized', tracking=True)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            if self.job_id.monetization_sena_id:
                self.contract_is_sena = True
            else:
                self.contract_is_sena = False

    @api.onchange('job_id')
    def _onchange_contract_is_sena(self):
        if self.job_id.monetization_sena_id.id:
            self.contract_is_sena = True

    @api.depends('type_apprentice_sena')
    @api.onchange('type_apprentice_sena', 'finish_date_productive_sena', 'finish_date_lective_sena')
    def _compute_state_contract_sena(self):
        for contract in self:
            if contract.finish_date_productive_sena and contract.finish_date_lective_sena:

                if contract.type_apprentice_sena == 'lective':
                    contract.days_to_finalized = (contract.finish_date_lective_sena - date.today()).days
                if contract.type_apprentice_sena == 'productive':
                    contract.days_to_finalized = (contract.finish_date_productive_sena - date.today()).days

                if contract.days_to_finalized > 30:
                    contract.state_contract_sena = 'running'
                if contract.days_to_finalized <= 30:
                    contract.state_contract_sena = 'to_finalize'
                if contract.days_to_finalized <= 0:
                    contract.state_contract_sena = 'finalized'
