from odoo import api, fields, models


class ZPrenominaWizard(models.TransientModel):
    _name = 'zprenomina.report.wizard'

    employee_ids = fields.Many2many('hr.employee', string='Employees')
    company_ids = fields.Many2many('res.company', string="Companies")
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    all_employees = fields.Boolean('All Employees', default=False)

    @api.onchange('all_employees')
    def onchange_all_employees(self):
        if self.all_employees == True:
            self.employee_ids = self.env['hr.employee'].search([('company_id', 'in', self.company_ids.ids)])