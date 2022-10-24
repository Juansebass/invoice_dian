
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    """Add Fields."""
    _inherit = 'res.company'

    icbf = fields.Boolean()
    icbf_rate = fields.Float()
    benefit_ccf = fields.Boolean()
    sena = fields.Boolean()
    sena_rate = fields.Float()

    arl_id = fields.Many2one(
        'res.partner', 'ARL',
        domain="[('is_arl', '=', True)]")
