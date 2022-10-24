from odoo import api, fields, models


class CenterCost(models.Model):
    _inherit = 'hr.center.cost'

    employee_substitution_id = fields.Many2one('hr.employee.substitution', 'Employer Substitution')


class NewCenterCost(models.Model):
    _inherit = 'hr.new.center.cost'

    employee_substitution_id = fields.Many2one('hr.employee.substitution', 'Employer Substitution')


class HrContractFlexWage(models.Model):
    _inherit = 'hr.contract.flex_wage'

    hr_employee_substitution_id = fields.Many2one('hr.employee.substitution')
