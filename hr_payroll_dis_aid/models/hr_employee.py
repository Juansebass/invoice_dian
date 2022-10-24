from odoo import api, fields, models, exceptions, _


class Employee(models.Model):
    _inherit = 'hr.employee'

    dis_aid_count = fields.Integer(compute='compute_dis_aid')

    def get_dis_aid(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Discounts / Aids',
            'view_mode': 'tree,form',
            'res_model': 'hr.payroll.dis.aid',
            'domain': [('employee_id', '=', self.id), ('state', 'in', ('draft', 'approved'))],
            'context': "{'create': False}"
        }

    def compute_dis_aid(self):
        for record in self:
            record.dis_aid_count = self.env['hr.payroll.dis.aid'].search_count(
                [('employee_id', '=', self.id), ('state', 'in', ('draft', 'approved'))])

    def get_balance_from_dis_aid(self, event, def_return=True):
        """Get current balance from dia/aid records for the selected employee."""

        event_id = self.env['hr.pv.event'].search([('name', '=', event)])
        if len(event_id) > 1:
            event_id = event_id.filtered(lambda x: x.company_id == self.env.company
                                                   or x.company_id == False)

            if len(event_id) > 1:
                raise exceptions.ValidationError(
                    _('The name is in two events you must only one event with this name.'))

        if not event_id:
            event_id = self.env['hr.pv.event'].search([('code', '=', event)])
            if len(event_id) > 1:
                raise exceptions.ValidationError(
                    _('The code is in two events you must only one event with this code.'))

        amount = 0
        if event_id:
            concept_ids = self.env['hr.payroll.dis.aid.concept'].search([('event_id', '=', event_id.id)])

            """
            dis_aid_ids = self.env['hr.payroll.dis.aid'].search(
                [('control_balance', '=', True),
                 ('employee_id', '=', self.id),
                 ('capital_to_pay', '>', 0),
                 ('state', '=', 'approved'),
                 ('concept_id', 'in', concept_ids.ids)])
            """
            dis_aid_ids = self.env['hr.payroll.dis.aid'].search(
                [('employee_id', '=', self.id),
                 ('state', '=', 'approved'),
                 ('concept_id', 'in', concept_ids.ids)])

            # [amount += dis_aid.capital_to_pay for dis_aid in dis_aid_ids]
            for dis_aid in dis_aid_ids:
                amount += dis_aid.capital_to_pay

            if def_return:
                return amount * -1
            else:
                return dis_aid_ids

        else:
            if def_return:
                return 0.0
            else:
                return False
