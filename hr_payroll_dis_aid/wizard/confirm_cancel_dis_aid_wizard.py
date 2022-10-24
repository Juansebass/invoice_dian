from odoo import api, fields, models


class ConfirmCancelDisAids(models.TransientModel):
    _name = 'hr.dis.aid.confirm.cancel'

    def action_cancel(self):
        aids = self.env['hr.payroll.dis.aid'].browse(self.env.context['active_ids'])
        if aids:
            aids.action_cancel()
