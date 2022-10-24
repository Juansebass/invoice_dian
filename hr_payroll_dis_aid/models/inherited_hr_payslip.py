# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import api, models, fields, tools, _
from datetime import datetime
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()

        for slip in self:
            pv_payed = []

            '''Validate if process is contract completion or like a regular slip'''
            if not slip.contract_completion_id:
                for slip_line in slip.line_ids:
                    rule_value = slip_line.amount

                    for pv in slip_line.pv_ids.filtered(lambda x: x.amount != 0):

                        if pv not in pv_payed:
                            pv_payed.append(pv)

                            pv_value = pv.amount

                            dis_aid_line_id = self.env['hr.payroll.dis.aid.line'].search([('pv_id', '=', pv.id)])

                            if dis_aid_line_id:
                                dis_aid_line_id.write({
                                    'state': 'payed',
                                })

                                payment_line = dis_aid_line_id.dis_aid_id.create_dis_aid_payment_line(
                                    dis_aid_id=dis_aid_line_id.dis_aid_id.id,
                                    dis_aid_line_id=dis_aid_line_id.id,
                                    name=slip.name,
                                    date=datetime.today(),
                                    payment_value=pv_value * -1 if slip_line.slip_id.credit_note else pv_value,
                                    payslip_line_id=slip_line.id,

                                )

                            rule_value -= pv.amount

                    total_percentage = 0
                    rule_remain_value = rule_value
                    for pv in slip_line.pv_ids.filtered(lambda x: x.percentage != 0):
                        total_percentage += pv.percentage

                    for pv in slip_line.pv_ids.filtered(lambda x: x.percentage != 0):

                        if pv not in pv_payed:
                            pv_payed.append(pv)

                            pv_value = (rule_remain_value * total_percentage) / pv.percentage

                            dis_aid_line_id = self.env['hr.payroll.dis.aid.line'].search([('pv_id', '=', pv.id)])

                            if dis_aid_line_id:
                                dis_aid_line_id.write({
                                    'state': 'payed',
                                })

                                payment_line = dis_aid_line_id.dis_aid_id.create_dis_aid_payment_line(
                                    dis_aid_id=dis_aid_line_id.dis_aid_id.id,
                                    dis_aid_line_id=dis_aid_line_id.id,
                                    name=slip.name,
                                    date=datetime.today(),
                                    payment_value=pv_value * -1 if slip_line.slip_id.credit_note else pv_value,
                                    payslip_line_id=slip_line.id
                                )

                        rule_value -= pv.amount
            else:
                for slip_line in slip.line_ids:
                    rule_value = slip_line.amount

                    for dis_aid_id in slip_line.dis_aid_ids:
                        if dis_aid_id.control_balance:
                            dis_aid_value = dis_aid_id.capital_to_pay
                        else:
                            dis_aid_value = 0

                        payment_line = dis_aid_id.create_dis_aid_payment_line(
                            dis_aid_id=dis_aid_id.id,
                            dis_aid_line_id=False,
                            name=slip.name,
                            date=datetime.today(),
                            payment_value=dis_aid_value * -1 if slip_line.slip_id.credit_note else dis_aid_value,
                            payslip_line_id=slip_line.id,
                        )

                        if not dis_aid_id.control_balance:
                            dis_aid_id.action_finish()

                        rule_value -= dis_aid_value

                        dis_aid_line_id = self.env['hr.payroll.dis.aid.line'].search([('pv_id', '=', pv.id)])

                        if dis_aid_line_id:
                            dis_aid_line_id.write({
                                'state': 'payed',
                            })
        return res


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"

    dis_aid_ids = fields.Many2many(
        'hr.payroll.dis.aid', 'hr_payslip_hr_payroll_dis_aid_rel',
        'payslip_line_id', 'dis_aid_id', string='Dis/Aid')

    contract_completion_id = fields.Many2one('hr.contract.completion', related='slip_id.contract_completion_id')
