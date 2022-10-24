
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
#remove

class HrContract(models.Model):
    """Add Risk Type."""
    _inherit = "hr.contract"

    risk_type_id = fields.Many2one('hr.risk.type', 'Risk Type')

    @api.onchange('risk_type_id')
    def onchange_risk_type_id(self):
        """Fill ARL Percentage."""
        if self.risk_type_id:
            self.arl_percentage = self.risk_type_id.percentage
