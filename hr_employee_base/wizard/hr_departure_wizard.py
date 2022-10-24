
# -*- coding: utf-8 -*-
from odoo import fields, models



class HrDepartureWizard(models.TransientModel):
    _inherit = "hr.departure.wizard"
    
    def action_register_departure(self):
        res = super(HrDepartureWizard,self).action_register_departure()
        employee = self.employee_id
        employee.fourth_name = employee.fourth_name + ' ARCHIVADO'
        employee.name = employee.name + ' ARCHIVADO'
        return res
