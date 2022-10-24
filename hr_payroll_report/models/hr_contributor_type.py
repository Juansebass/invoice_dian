
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class HrContributorType(models.Model):
    """Hr Risk Type."""
    _name = "hr.contributor.type"

    name = fields.Char()
    code = fields.Char()
