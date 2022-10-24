
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResPartner(models.Model):
    """Add Fields."""
    _inherit = 'res.partner'

    contributor_class = fields.Selection(
        [('1', 'Contributor with 200 or more contributors'),
         ('2', 'Contributor with less than 200 contributors'),
         ('3', 'Mipyme contributor that takes advantage of Law 590 of 2000'),
         ('4', 'Beneficiary contributor of article 5 of Law 1429 of 2010'),
         ('5', 'Independent')])
    legal_nature = fields.Selection(
        [('1', 'Pública'),
         ('2', 'Privada'),
         ('3', 'Mixta'),
         ('4', 'Organismos multilaterales'),
         ('5', 'Entidades de derecho público no sometidas a la legislación colombiana')])
    person_pila_type = fields.Selection(
        [('N', 'Natural'),
         ('J', 'Jurídica')])

    ciiu = fields.Many2many('ciiu.value', string="CIIU")

    commercial_register = fields.Char()
    commercial_register_date = fields.Date()
    code_found_layoffs = fields.Char()
    code_compensation_box = fields.Char()
    code_eps = fields.Char()
    code_required_physical_evidence = fields.Char()
    code_unemployee_fund = fields.Char()
    code_arl = fields.Char()
    code_prepaid_medicine = fields.Char()
    code_afc = fields.Char()
    code_afp = fields.Char()
    code_voluntary_contribution = fields.Char()


class CiiuValue(models.Model):
    _name = 'ciiu.value'

    name = fields.Char('Descripción')
    code = fields.Char('Código')
    company_id = fields.Many2one('res.company')
