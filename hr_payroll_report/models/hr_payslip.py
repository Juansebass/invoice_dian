from odoo import api, fields, models


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def get_totals(self):
        line_ids = self.line_ids
        total_accruals = 0
        total_deductions = 0
        totals = []

        for line in line_ids:
            if line.amount > 0:
                total_accruals += line.amount
            else:
                total_deductions += line.amount

        lines = {
            'total_accruals': int(total_accruals),
            'total_deductions': int(total_deductions),
            'total_net': int(total_accruals - abs(total_deductions))
        }

        totals.append(lines)

        return totals
