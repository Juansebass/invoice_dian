# -*- coding: utf-8 -*-
from odoo import fields,models


class ResUser(models.Model):
    _inherit = "res.users"

    is_recruitment_leader = fields.Boolean('Lider de selección')
