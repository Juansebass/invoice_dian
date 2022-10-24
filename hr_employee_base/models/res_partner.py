# -*- coding: utf-8 -*-
from odoo import fields,models,api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # first_name = fields.Char('Primer Nombre', tracking=1)
    # second_name = fields.Char('Segundo Nombre', tracking=2)
    # first_surname = fields.Char('Primer Apellido', tracking=3)
    # second_surname = fields.Char('Segundo Apellido',tracking=4)

    identifier = fields.Char('Identificador')
    ugpp_type = fields.Selection([('AFP', 'AFP'),('AFC', 'AFC'),('ARL','ARL'),('EPS','EPS'),('CCF','CAJA DE COMPENSACIÓN')],tracking=5, string="Clasificación UGPP")

    is_found_layoffs = fields.Boolean(string='Found Layoffs')
    is_ccf = fields.Boolean(string='Compensation Box')
    is_eps = fields.Boolean(string='EPS')
    required_physical_evidence = fields.Boolean(string='Required Physical Evidence')
    is_unemployee_fund = fields.Boolean(string='Unemployee Fund')
    is_arl = fields.Boolean(string='ARL')
    is_prepaid_medicine = fields.Boolean(string='Prepaid Medicine')
    is_afc = fields.Boolean(string='AFC')
    is_voluntary_contribution = fields.Boolean(string='Voluntary Contribution')
    is_afp = fields.Boolean(string='AFP')


class ResGender(models.Model):
    _name = "res.gender"
    _description = 'Gender'

    name = fields.Char('Género')
