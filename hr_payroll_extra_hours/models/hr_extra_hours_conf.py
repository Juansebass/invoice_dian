from odoo import fields, models


class HrExtraHoursConf(models.Model):
    """Hr Extra Hours Conf."""

    _name = "hr.extra.hours.conf"

    name = fields.Char('Extra Value')
    factor = fields.Float()
    extra_factor = fields.Float()
