# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    legal_representative_id = fields.Many2one('hr.employee', 'Representative')
    create_default_employee = fields.Boolean('Create Default Employee?')
