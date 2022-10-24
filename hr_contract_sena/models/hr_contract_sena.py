from odoo import fields, models, api, _


class HrContractSena(models.Model):
    _name = 'hr.contract.sena'
    _description = 'Model in order to identify Sena apprentices'

    company_id = fields.Many2one('res.company', string='Company', required=True,
                                 default=lambda self: self.env.company.id)

    number_mandatory_practitioners = fields.Integer(string='Number of Mandatory Practitioners', default=0)
    number_current_practitioners = fields.Integer(string='Number of Current Practitioners', )
    status = fields.Boolean(string='Status', default=False)

    employee_number = fields.Integer('No. Resolution Employees')
    number_apprentices = fields.Integer('No. Resolution Apprentices')
    days_monetize = fields.Integer('Days Monetize')
    number_apprentices_plant = fields.Integer('Number of Apprentices in Plant')
    number_apprentices_to_monetized = fields.Integer('Number of Apprentices to be Monetized')
    support_days = fields.Integer('Support Days')
    days_to_monetize = fields.Integer('Days to Monetize')
    monetize_value = fields.Float('V/r Monetize')
    monetize_invoice_value = fields.Float('V/r Monetize Invoice')

    resolution_status = fields.Char(string='Status Resolution', required=False)

    @api.model
    def default_record(self):
        id = self.env['hr.contract.sena'].search([])[0]
        return {
            'name': _('Contracts Sena Count'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract.sena',
            'view_mode': 'form',
            # 'context': {'default_id': id},
            'view_id': self.env.ref('hr_contract_sena.board_hr_contract_sena_view_form').id
        }

    @api.onchange('company_id')
    @api.depends('company_id')
    def default_data(self):
        self.employee_number = 0
        self.number_apprentices = 0
        self.days_to_monetize = 0
        self.days_monetize = 0
        self.number_apprentices_plant = 0
        self.support_days = 0
        self.number_apprentices_to_monetized = 0
        self.monetize_value = 0
        self.monetize_invoice_value = 0

        employees = self.env['hr.employee'].search([('company_id', '=', self.company_id.id)])
        apprentices = (
            self.env['hr.contract'].search([('contract_is_sena', '=', True), ('company_id', '=', self.company_id.id),
                                            ('state', '=', 'open')]))
        today = fields.Date.today()
        config = self.env['hr.payroll.config'].search(
            [('start_date', '<=', today), ('end_date', '>=', today), ('state', '=', 'done')])
        min_salary = self.env['hr.payroll.config.lines'].search(
            [('hr_payroll_config_id', '=', config.id), ('variable.name', '=', 'Salario Minimo')])

        if employees:
            self.employee_number = len(employees)
            if self.employee_number >= 20:
                self.number_apprentices = round(len(employees) / 20)

            if self.employee_number >= 15 and self.employee_number <= 19:
                self.number_apprentices = 1

            if self.number_apprentices > 0:
                self.days_monetize = self.number_apprentices * 30
                self.number_apprentices_plant = len(apprentices)
                self.number_apprentices_to_monetized = abs(self.number_apprentices - self.number_apprentices_plant)
                self.support_days = self.number_apprentices_plant * 30
                self.days_to_monetize = abs(self.days_monetize - self.support_days)
                self.monetize_value = (self.days_to_monetize * min_salary.value) / 30
                self.monetize_invoice_value = (
                                                      self.employee_number * 0.05 * min_salary.value) / self.number_apprentices / 30 * self.days_to_monetize
