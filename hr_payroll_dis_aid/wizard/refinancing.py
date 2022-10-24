from odoo import api, fields, models, exceptions, _
import math
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError, Warning

TYPE = [('extra_pay', 'Extra Quote Pay'), ('refinance', 'Refinance')]


class HrPayrollDisAidRefinancing(models.TransientModel):
    _name = 'hr.dis.aid.refinancing'

    type = fields.Selection(string='Type', selection=TYPE, required=True)
    extra_quote_value = fields.Float('Extra Quote Value')
    new_term_in_months = fields.Integer('Term in Month')

    def refinancing(self):
        aids = self.env['hr.payroll.dis.aid'].browse(self.env.context['active_ids'])

        for dis in aids:
            if self.type == 'extra_pay':
                if self.extra_quote_value and self.extra_quote_value <= 0:
                    raise UserError(_('You must enter the extra value to be paid.'))

                # if aids.total_payable < self.extra_quote_value:
                if dis.control_balance and dis.capital_to_pay < self.extra_quote_value:
                    raise UserError(_('Extra payment value is greater than the balance.'))

                payment_line = dis.create_dis_aid_payment_line(
                    dis_aid_id=dis.id,
                    dis_aid_line_id=False,
                    name=_('Extra payment'),
                    date=datetime.today(),
                    payment_value=self.extra_quote_value,
                    payslip_line_id=False
                )

            if self.type == 'refinance':
                dis.recalc_quotes_with_new_balance(quotes=self.new_term_in_months)
