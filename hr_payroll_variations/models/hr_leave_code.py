# -*- coding: utf-8 -*-


from odoo import fields, models


class HrLeaveCode(models.Model):
    """Hr Leave Code."""

    _name = 'hr.leave.code'
    _description = 'Hr Leave Code'
    _rec_name = 'code'

    name = fields.Char()
    code = fields.Char()
