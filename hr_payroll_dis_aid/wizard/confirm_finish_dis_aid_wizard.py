from odoo import api, fields, models


class ConfirmFinishDisAids(models.TransientModel):
    _name = 'hr.dis.aid.confirm.finish'

    def action_finish(self):
        aids = self.env['hr.payroll.dis.aid'].browse(self.env.context['active_ids'])
        if aids:
            aids.action_finish()
