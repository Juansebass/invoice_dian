from odoo import api, fields, models, _

class PaymentType(models.Model):
    _name = 'payment.type'
    _description = 'Payment Type'


    name = fields.Char(string='Name')
    code = fields.Char(string='Code')
    bank_id = fields.Many2one('res.bank', string='Bank')
    active = fields.Boolean(default=True)


    _sql_constraints = [
		('name_unique', 'unique(name)', _("The name must be unique")),
		('code_unique', 'unique(code, bank_id)', _("The code must be unique per bank"))]

#