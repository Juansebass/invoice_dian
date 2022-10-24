from odoo import api, fields, models, _
from datetime import date
from datetime import datetime


class DebtCapacityWizard(models.Model):
    _name = 'debt.capacity.wizard'
    _description = 'Debt Capacity Wizard'

    concept_id = fields.Many2one(comodel_name='hr.payroll.dis.aid.concept', string='Concept', required=True)

    def create_discount(self):
        active_id = self.env.context.get('active_id')
        debt_capacity_id = self.env['hr.payroll.debt.capacity'].browse(self.env.context['active_ids'])

        discount = self.env['hr.payroll.dis.aid'].create({
            'employee_id': debt_capacity_id.employee_id.id,
            'identification_id': debt_capacity_id.identification_id,
            'debt_capacity_id': debt_capacity_id.id,
            'concept_id': self.concept_id.id,
            'total': debt_capacity_id.requested_amount,
            'monthly_fee': 0,
            'total_amount': 0,
            'date': date.today()
        })

        debt_capacity_id.state = 'finalized'

        return {
            'name': _('Discount Created'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.payroll.dis.aid',
            'view_id': self.env.ref('hr_payroll_dis_aid.hr_payroll_dis_aid_view_form').id,
            'target': 'current',
            'res_id': discount.id,
        }
