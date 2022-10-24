from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_court = fields.Boolean('Court')
