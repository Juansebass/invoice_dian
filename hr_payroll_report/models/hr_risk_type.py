
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrRiskType(models.Model):
    """Hr Risk Type."""
    _name = "hr.risk.type"

    code = fields.Char()
    name = fields.Char()
    percentage = fields.Float()
