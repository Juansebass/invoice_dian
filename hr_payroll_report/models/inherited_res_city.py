
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCity(models.Model):
    """Add Fields."""
    _inherit = 'res.city'

    div_code = fields.Char()
