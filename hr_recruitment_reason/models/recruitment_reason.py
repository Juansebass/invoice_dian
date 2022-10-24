# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class RecruitmentReason(models.Model):
    _name = "hr.recruitment.reason"
    _description = 'Recruitment Reason'

    name = fields.Char('Name')
    description = fields.Text('Description')
    abbreviation = fields.Char('Abbreviation')
