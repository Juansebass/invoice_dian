# -*- coding: utf-8 -*-
# Copyright 2021 Diego Carvajal <Github@diegoivanc>


from odoo import api, models, fields, _
from odoo.exceptions import UserError

import logging

_logger = logging.getLogger(__name__)
class ResPartner(models.Model):
	_inherit = "res.partner"

	def _get_accounting_partner_party_values(self, company_id):
		msg1 = _("'%s' does not have a person type established.")
		msg2 = _("'%s' does not have a city established.")
		msg3 = _("'%s' does not have a state established.")
		msg4 = _("'%s' does not have a country established.")
		msg5 = _("'%s' does not have a verification digit established.")
		msg6 = _("'%s' does not have a DIAN document type established.")
		msg7 = _("'%s' does not have a identification document established.")
		msg8 = _("'%s' does not have a fiscal position correctly configured.")
		msg9 = _("'%s' does not have a fiscal position established.")
		msg10 = _("E-Invoicing Agent: '%s' does not have a E-Invoicing Email.")
		msg11 = _("The partner '%s' does not have a Email.")
		name = self.name
		zip_code = False
		identification_document = self._get_vat_without_verification_code()
		first_name = False
		family_name = False
		middle_name = False
		telephone = False


        
		"""
		if not self.person_type:
			raise UserError(msg1 % self.name)

		if self.country_id:
			if self.country_id.code == 'CO' and not self.zip_id:
				raise UserError(msg2 % self.name)
			elif self.country_id.code == 'CO' and not self.state_id:
				raise UserError(msg3 % self.name)
		else:
			raise UserError(msg4 % self.name)
		"""

		if self.l10n_latam_identification_type_id:
			document_type_code = self._l10n_co_edi_get_carvajal_code_for_identification_type()

			if document_type_code == '31' and not self._get_vat_verification_code():
				raise UserError(msg5 % self.name)

			"""
			#Punto 13.2.1. del anexo técnico version 1.8
			if document_type_code not in ('11', '12', '13', '21', '22', '31', '41', '42', '50', '91'):
				if self.person_type == '1':
					raise UserError(msg6 % self.name)
				else:
					name = 'usuario final'
					document_type_code = '13'
					identification_document = '2222222222'
			"""
		else:
			raise UserError(msg6 % self.name)


		if not self._get_vat_without_verification_code():
			raise UserError(msg7 % self.name)

		if not self.email:
			raise UserError(msg11 % self.name)
		if self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen:
			if (not self.with_company(self.company_id.id or company_id).l10n_co_edi_obligation_type_ids):
				raise UserError(msg8 % self.name)

		tax_level_codes = ''
		for tax_level_code_id in self.with_company(self.company_id.id or company_id).l10n_co_edi_obligation_type_ids:
			if tax_level_codes == '':
				tax_level_codes = tax_level_code_id.name
			else:
				tax_level_codes += ';' + tax_level_code_id.name


		"""
		if self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen:
			if (not self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_level_code_id
					or not self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_scheme_id
					or not self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.listname):
				raise UserError(msg8 % self.name)

			tax_level_codes = ''
			tax_scheme_code = self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_scheme_id.code
			tax_scheme_name = self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_scheme_id.name
		else:
			raise UserError(msg9 % self.name)


		for tax_level_code_id in self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_level_code_id:
			if tax_level_codes == '':
				tax_level_codes = tax_level_code_id.code
			else:
				tax_level_codes += ';' + tax_level_code_id.code

		if self.firstname:
			first_name = self.firstname
			middle_name = self.othernames
		else:
			first_name = self.othernames

		if self.lastname and self.lastname2:
			family_name = self.lastname + self.lastname2
		elif self.lastname:
			family_name = self.lastname
		elif self.lastname2:
			family_name = self.lastname2

		if self.phone and self.mobile:
			telephone = self.phone + " / " + self.mobile
		elif self.lastname:
			telephone = self.phone
		elif self.lastname2:
			telephone = self.mobile
		"""

		return {
			'AdditionalAccountID': self._l10n_co_edi_get_partner_type(),
			'PartyName': self.l10n_co_edi_commercial_name,
			'Name': self.name,
			'AddressID': self.city_id.l10n_co_edi_code or '',
			'AddressCityName':  self.city_id.name or '',
			'AddressPostalZone': self.zip or '',
			'AddressCountrySubentity': self.state_id.name,
			'AddressCountrySubentityCode': self.state_id.l10n_co_edi_code,
			'AddressLine': self.street or '',
			'CompanyIDschemeID': self._get_vat_verification_code(),
			'CompanyIDschemeName': self._l10n_co_edi_get_carvajal_code_for_identification_type(),
			'CompanyID': self._get_vat_without_verification_code(),
			'listName': self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen,
			'TaxLevelCode': tax_level_codes,
			# self.with_company(self.company_id.id or company_id).property_account_position_id.tax_level_code_id.code,
			#'TaxSchemeID': self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_scheme_id.code,
			#'TaxSchemeName': self.with_company(self.company_id.id or company_id).l10n_co_edi_fiscal_regimen.tax_scheme_id.name,
			'TaxSchemeID': '01',
			'TaxSchemeName': 'IVA',
			'CorporateRegistrationSchemeName': self.ref,
			'CountryIdentificationCode': self.country_id.code,
			'CountryName': self.country_id.name,
			'FirstName': first_name,
			'FamilyName': family_name,
			'MiddleName': middle_name,
			'Telephone': telephone,
			'Telefax': '',
			'ElectronicMail': self.email,
		}


	def _get_tax_representative_party_values(self):
		msg1 = _("'%s' does not have a DIAN document type established.")
		msg2 = _("'%s' does not have a identification document established.")
		msg3 = _("'%s' does not have a verification digit established.")
		if not self.l10n_latam_identification_type_id:
			raise UserError(msg1 % self.name)
		if not self._get_vat_without_verification_code():
			raise UserError(msg2 % self.name)
		if self._l10n_co_edi_get_carvajal_code_for_identification_type() == '31' and not self._get_vat_verification_code():
			raise UserError(msg3 % self.name)

		return {
			'IDschemeID': self._get_vat_verification_code() or '',
			'IDschemeName': self._l10n_co_edi_get_carvajal_code_for_identification_type(),
			'ID': self._get_vat_without_verification_code()}

	def _get_delivery_values(self):
		msg1 = _("'%s' does not have a city established.")
		msg2 = _("'%s' does not have a state established.")
		msg3 = _("'%s' does not have a country established.")
		zip_code = False

		"""
		if self.country_id:
			if self.country_id.code == 'CO':
				if not self.zip_id:
					raise UserError(msg1 % self.name)
				elif not self.state_id:
					raise UserError(msg2 % self.name)
		else:
			raise UserError(msg3 % self.name)
		"""

		return {
			'AddressID': self.city_id.l10n_co_edi_code or '',
			'AddressCityName': self.city_id.name or '',
			'AddressPostalZone': self.zip or '',
			'AddressCountrySubentity': self.state_id.name or '',
			'AddressCountrySubentityCode': self.state_id.l10n_co_edi_code or '',
			'AddressLine': self.street or '',
			'CountryIdentificationCode': self.country_id.code,
			'CountryName': self.country_id.name
        }
