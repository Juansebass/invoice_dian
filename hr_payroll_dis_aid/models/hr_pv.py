from odoo import api, fields, models


class HrPv(models.Model):
    _inherit = 'hr.pv'

    # """Discounts relation Field"""
    is_dis_aid = fields.Boolean(string='Is_dis_aid', default=False, required=False)
    dis_aid_id = fields.Many2one(comodel_name='hr.payroll.dis.aid', string='Discount/Aid', required=False)

    @api.model
    def _unique_pv_domain(self, employee, event, start_date, amount):
        domain = super(HrPv, self)._unique_pv_domain(employee, event, start_date, amount)
        domain.append(('dis_aid_id', '=', False))
        return domain
