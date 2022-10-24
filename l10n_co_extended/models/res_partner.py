# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions
from odoo.exceptions import ValidationError
from odoo.osv import expression
import re
import logging
_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    

    name = fields.Char(
        compute="_compute_name",
        inverse="_inverse_name_after_cleaning_whitespace",
        required=False,
        store=True,
        readonly=False,)
    firstname = fields.Char("Primer Nombre", index=True)
    othernames = fields.Char("Otros Nombres")
    lastname = fields.Char("Primer Apellido", index=True)
    lastname2 = fields.Char("Segundo Apellido")
    detailed_address = fields.Boolean('Dirección detallada', default=True)
    co_street_1 = fields.Char()
    co_street_2 = fields.Char()
    co_street_3 = fields.Char()
    co_street_4 = fields.Char()
    co_street_5 = fields.Char()
    
    @api.model
    def _get_computed_name(self, firstname, othernames, lastname, lastname2):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of lastname and
        firstname the computed name"""
        order = self._get_names_order()
        
        if order == "last_first_comma":
            names = []
            if lastname:
                names.append(lastname)
            if lastname2:
                names.append(lastname2)
            if names and (firstname or othernames):
                names[-1] = names[-1] + ","
            if firstname:
                names.append(firstname)
            if othernames:
                names.append(othernames)
            return " ".join(p for p in names if p)
        elif order == "first_last":
            return " ".join(p for p in (firstname, othernames, lastname, lastname2) if p)
        else:
            return " ".join(p for p in (lastname, lastname2, firstname, othernames) if p)

    @api.depends("firstname", "othernames", "lastname", "lastname2")
    def _compute_name(self):
        """Write the 'name' according to splitted data."""
        for partner in self:
            partner.name = self._get_computed_name(
                partner.firstname, partner.othernames, partner.lastname, partner.lastname2)

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if not args:
            args = []
        criteria_operator = ['|'] if operator not in expression.NEGATIVE_TERM_OPERATORS else ['&', '!']
        domain = criteria_operator + [('vat', '=ilike', name + '%'), ('name', operator, name)]
        return self.search(domain + args, limit=limit).name_get()

    @api.model
    def create(self, vals):
        """Add inverted names at creation if unavailable."""
        context = dict(self.env.context)
        name = vals.get("name", context.get("default_name"))

        if name is not None:
            # Calculate the splitted fields
            inverted = self._get_inverse_name(
                self._get_whitespace_cleaned_name(name),
                vals.get("is_company", self.default_get(["is_company"])["is_company"]),
            )
            for key, value in inverted.items():
                if not vals.get(key) or context.get("copy"):
                    vals[key] = value

            # Remove the combined fields
            if "name" in vals:
                del vals["name"]
            if "default_name" in context:
                del context["default_name"]

        return super(ResPartner, self.with_context(context)).create(vals)

    def copy(self, default=None):
        """Ensure partners are copied right.

        Odoo adds ``(copy)`` to the end of :attr:`~.name`, but that would get
        ignored in :meth:`~.create` because it also copies explicitly firstname
        and lastname fields.
        """
        return super(ResPartner, self.with_context(copy=True)).copy(default)

    @api.model
    def default_get(self, fields_list):
        """Invert name when getting default values."""
        result = super(ResPartner, self).default_get(fields_list)

        inverted = self._get_inverse_name(self._get_whitespace_cleaned_name(result.get("name", "")),
                                          result.get("is_company", False),)

        for field in list(inverted.keys()):
            if field in fields_list:
                result[field] = inverted.get(field)

        return result

    @api.model
    def _names_order_default(self):
        return 'first_last'

    def _inverse_name(self):
        """Try to revert the effect of :meth:`._compute_name`."""
        for record in self:
            parts = record._get_inverse_name(record.name, record.is_company)
            record.lastname = parts['lastname']
            record.lastname2 = parts['lastname2']
            record.firstname = parts['firstname']
            record.othernames = parts['othernames']

    @api.model
    def _get_names_order(self):
        """Get names order configuration from system parameters.
        You can override this method to read configuration from language,
        country, company or other"""
        return (self.env["ir.config_parameter"].sudo().get_param("partner_names_order", self._names_order_default()))

    def _inverse_name_after_cleaning_whitespace(self):
        """Clean whitespace in :attr:`~.name` and split it.

        The splitting logic is stored separately in :meth:`~._inverse_name`, so
        submodules can extend that method and get whitespace cleaning for free.
        """
        for record in self:
            # Remove unneeded whitespace
            clean = record._get_whitespace_cleaned_name(record.name)
            record.name = clean
            record._inverse_name()

    @api.model
    def _get_whitespace_cleaned_name(self, name, comma=False):
        """Remove redundant whitespace from :param:`name`.

        Removes leading, trailing and duplicated whitespace.
        """
        try:
            name = " ".join(name.split()) if name else name
        except UnicodeDecodeError:
            # with users coming from LDAP, name can be a str encoded as utf-8
            # this happens with ActiveDirectory for instance, and in that case
            # we get a UnicodeDecodeError during the automatic ASCII -> Unicode
            # conversion that Python does for us.
            # In that case we need to manually decode the string to get a
            # proper unicode string.
            name = " ".join(name.decode("utf-8").split()) if name else name

        if comma:
            name = name.replace(" ,", ",")
            name = name.replace(", ", ",")
        return name

    @api.model
    def _get_inverse_name(self, name, is_company=False):
        """Compute the inverted name.

        - If the partner is a company, save it in the lastname.
        - Otherwise, make a guess.

        This method can be easily overriden by other submodules.
        You can also override this method to change the order of name's
        attributes

        When this method is called, :attr:`~.name` already has unified and
        trimmed whitespace.
        """
        # Company name goes to the lastname
        result = {
            'firstname': False,
            'othernames': False,
            'lastname': name or False,
            'lastname2': False,
        }
#         if not is_company and name:
#             order = self._get_names_order()
#             # Remove redundant spaces
#             name = self._get_whitespace_cleaned_name(
#                 name, comma=(order == "last_first_comma")
#             )
#             parts = name.split("," if order == "last_first_comma" else " ", 1)
#             if len(parts) > 1:
#                 if order == "first_last":
#                     parts = [" ".join(parts[1:]), parts[0]]
#                 else:
#                     parts = [parts[0], " ".join(parts[1:])]
#             else:
#                 while len(parts) < 2:
#                     parts.append(False)
#             result = {"lastname": parts[0], "firstname": parts[1]}
#             parts = []
#             # ___________________
#             if order == 'last_first':
#                 if result['firstname']:
#                     parts = result['firstname'].split(" ", 1)
#                 while len(parts) < 2:
#                     parts.append(False)
#                 result['lastname2'] = parts[0]
#                 result['firstname'] = parts[1]
#             else:
#                 if result['lastname']:
#                     parts = result['lastname'].split(" ", 1)
#                 while len(parts) < 2:
#                     parts.append(False)
#                 result['lastname'] = parts[0]
#                 result['lastname2'] = parts[1]
#             # ___________________
#             if order == 'first_last':
#                 if result['lastname2']:
#                     parts = result['lastname2'].split(" ", 1)
#                 while len(parts) < 2:
#                     result['othernames'] = False
#                     return result
#                 result['othernames'] = result['lastname']
#                 result['lastname'] = parts[0]
#                 result['lastname2'] = parts[1]
#             else:
#                 if result['firstname']:
#                     parts = result['firstname'].split(" ", 1)
#                 while len(parts) < 2:
#                     parts.append(False)
#                 result['firstname'] = parts[0]
#                 result['othernames'] = parts[1]
        return result
    
    # Disabling SQL constraint givint a more explicit error using a Python
    # contstraint
    _sql_constraints = [("check_name", "CHECK( 1=1 )", "Contacts require a name.")]

    @api.model
    def _concat_args(self, *argv):
        args = tuple(filter(lambda x: x, argv))
        return " ".join(map(str.upper, args))

    #concatenación Dirección tipo DIAN
    @api.onchange('co_street_1', 'co_street_2', 'co_street_3', 'co_street_4', 'co_street_5')                  
    def _onchange_street_fields(self):
        self.street = self._concat_args(
            self.co_street_1,
            self.co_street_2,
            self.co_street_3,
            self.co_street_4,
            self.co_street_5
        )