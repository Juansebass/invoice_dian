
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import base64
import calendar
import math

from odoo import api, fields, models, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

from odoo.tools import date_utils
from odoo.tools.misc import xlsxwriter
from datetime import timedelta, date
from io import BytesIO
import json


def round_up(number):
    if number > 0:
        number = math.ceil(number)
    return int(number)


def get_months():
    months_choices = []
    for month in range(1, 13):
        months_choices.append(
            (str(month), datetime.date(
                2019, month, 1).strftime('%B')))
    return months_choices


def get_years():
    years_choices = []
    for year in range(2020, 2101):
        years_choices.append(
            (str(year), str(year)))
    return years_choices


class HrPayrollPila(models.Model):
    """Hr Payroll Pila."""
    _name = "hr.payroll.pila"
    _rec_name = 'month'

    company_id = fields.Many2one('res.company', 'Company', required=True, default=lambda self: self.env.company,
                                 index=1)

    month = fields.Selection(get_months(), string="Month", required=True)
    year = fields.Selection(get_years(), string="Year", required=True)
    state = fields.Selection([
        ('initial', 'Initial'),
        ('draft', 'Draft'),
        ('process', 'Process'),
        ('done', 'Done')], string='Status', copy=False,
        default='initial')
    file1 = fields.Binary(copy=False)
    file1_name = fields.Char(string='Name', size=64, copy=False)
    file2 = fields.Binary(copy=False)
    file2_name = fields.Char(string='Name', size=64, copy=False)
    line1_ids = fields.One2many('hr.type2f1.line', 'hr_payroll_pila_id')
    line2_1_ids = fields.One2many('hr.type2f2_1.line', 'hr_payroll_pila_id')
    line2_2_ids = fields.One2many('hr.type2f2_2.line', 'hr_payroll_pila_id')
    log = fields.Text('Log', default='')
    check_log = fields.Boolean(default=False)

    def action_draft(self):
        for rec in self:
            rec.state = 'initial'

            rec.line1_ids.unlink()
            rec.line2_1_ids.unlink()

            rec.check_log = False
            rec.log = ''

            message = ''

            # Load data for File 1
            company_name = ''
            if rec.company_id.name:
                company_name = rec.company_id.name
            else:
                message = message + _(' - Company Name') + '\n'

            document_type = ''
            # cambio
            if rec.company_id.partner_id and rec.company_id.partner_id.l10n_latam_identification_type_id.name:
                document_type = rec.company_id.partner_id.l10n_latam_identification_type_id.name
            else:
                message = message + _(' - Document Type') + '\n'

            identification_number = ''
            # cambio
            # if rec.company_id.partner_id and rec.company_id.partner_id.identification_document:
            #     identification_number = rec.company_id.partner_id.identification_document
            if rec.company_id.partner_id and rec.company_id.partner_id._get_vat_without_verification_code():
                identification_number = rec.company_id.partner_id._get_vat_without_verification_code()
            else:
                message = message + _(' - Document Number') + '\n'

            verification_code = ''
            # cambio
            if rec.company_id.partner_id and rec.company_id.partner_id._get_vat_verification_code():
                verification_code = rec.company_id.partner_id._get_vat_verification_code()
            else:
                message = message + _(' - Verification Digit') + '\n'

            sucursal_code = ''
            sucursal_name = ''

            contributor_class = ''
            if rec.company_id.partner_id and rec.company_id.partner_id.contributor_class:
                contributor_class = rec.company_id.partner_id.contributor_class
            else:
                message = message + _(' - Contributor Class') + '\n'

            legal_nature = ''
            if rec.company_id.partner_id and rec.company_id.partner_id.legal_nature:
                legal_nature = rec.company_id.partner_id.legal_nature
            else:
                message = message + _(' - Legal Nature') + '\n'

            person_type = ''
            if rec.company_id.partner_id and rec.company_id.partner_id.person_pila_type:
                person_type = rec.company_id.partner_id.person_pila_type
            else:
                message = message + _(' - Person Type') + '\n'

            presentation_form = 'U'

            street = ''
            if rec.company_id.partner_id and rec.company_id.partner_id.street:  # complete_adress_dian:
                street = rec.company_id.partner_id.street  # complete_adress_dian
            else:
                message = message + _(' - Street') + '\n'

            divpola_code = ''
            if rec.company_id.partner_id.city_id and rec.company_id.partner_id.city_id.l10n_co_edi_code:
                divpola_code = str(rec.company_id.partner_id.city_id.l10n_co_edi_code)
            else:
                message = message + _(' - DiviPola Code') + '\n'

            state = ''
            if rec.company_id.partner_id.state_id and rec.company_id.partner_id.state_id.code:
                state = rec.company_id.partner_id.state_id.code
            else:
                message = message + _(' - State') + '\n'

            ica_activity = ''
            if rec.company_id.partner_id.ciiu and rec.company_id.partner_id.ciiu.code:
                ica_activity = rec.company_id.partner_id.ciiu.code
            else:
                message = message + _(' - ICA Activity') + '\n'

            phone = ''
            if rec.company_id.partner_id.phone and rec.company_id.partner_id.phone:
                phone = rec.company_id.partner_id.phone
            else:
                message = message + _(' - Phone Number') + '\n'

            mobile = ''
            if rec.company_id.partner_id.mobile and rec.company_id.partner_id.mobile:
                mobile = rec.company_id.partner_id.mobile
            else:
                message = message + _(' - Mobile') + '\n'

            email = ''
            if rec.company_id.partner_id.email and rec.company_id.partner_id.email:
                email = rec.company_id.partner_id.email
            else:
                message = message + _(' - E-Mail') + '\n'

            rl_document_type = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.partner_id._l10n_co_edi_get_carvajal_code_for_identification_type():
                rl_document_type = rec.company_id.legal_representative_id.partner_id._l10n_co_edi_get_carvajal_code_for_identification_type()
            else:
                message = message + _(' - Legal Representative Identification Type') + '\n'

            rl_identification_id = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.identification_id:
                rl_identification_id = rec.company_id.legal_representative_id.identification_id
            else:
                message = message + _(' - Legal Representative Identification Number') + '\n'

            rl_verification_code = '0'

            rl_third_name = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.third_name:
                rl_third_name = rec.company_id.legal_representative_id.third_name
            else:
                message = message + _(' - Legal Representative Third Name') + '\n'

            rl_fourth_name = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.fourth_name:
                rl_fourth_name = rec.company_id.legal_representative_id.fourth_name
            else:
                message = message + _(' - Legal Representative Fourth Name') + '\n'

            rl_first_name = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.first_name:
                rl_first_name = rec.company_id.legal_representative_id.first_name
            else:
                message = message + _(' - Legal Representative First Name') + '\n'

            rl_second_name = ''
            if rec.company_id.legal_representative_id and rec.company_id.legal_representative_id.second_name:
                rl_second_name = rec.company_id.legal_representative_id.second_name
            else:
                message = message + _(' - Legal Representative Second Name') + '\n'

            concordate_date = ''
            action_type = ''
            concordate_end_date = ''
            operator = ''
            payment_period = ''
            aportant_type = ''

            commercial_register_date = ''
            if rec.company_id.partner_id.commercial_register_date and rec.company_id.partner_id.commercial_register_date:
                commercial_register_date = rec.company_id.partner_id.commercial_register_date.strftime('%Y-%m-%d')
            else:
                message = message + _(' - Commercial Register Date') + '\n'

            icbf = 'N'
            if rec.company_id.icbf:
                icbf = 'S'

            benefit_ccf = 'N'
            if rec.company_id.benefit_ccf:
                benefit_ccf = 'S'

            line_one = self.env['hr.type2f1.line'].create({
                'company_name': company_name,
                'document_type': document_type,
                'identification_number': identification_number,
                'verification_code': verification_code,
                'sucursal_code': sucursal_code,
                'sucursal_name': sucursal_name,
                'contributor_class': contributor_class,
                'legal_nature': legal_nature,
                'person_type': person_type,
                'presentation_form': presentation_form,
                'street': street,
                'divpola_code': divpola_code,
                'state': state,
                'ica_activity': ica_activity,
                'phone': phone,
                'mobile': mobile,
                'email': email,
                'rl_identification_id': rl_identification_id,
                'rl_verification_code': rl_verification_code,
                'rl_document_type': rl_document_type,
                'rl_third_name': rl_third_name,
                'rl_fourth_name': rl_fourth_name,
                'rl_first_name': rl_first_name,
                'rl_second_name': rl_second_name,
                'concordate_date': concordate_date,
                'action_type': action_type,
                'concordate_end_date': concordate_end_date,
                'operator': operator,
                'payment_period': payment_period,
                'aportant_type': aportant_type,
                'commercial_register_date': commercial_register_date,
                'state_partner': state,
                'icbf': icbf,
                'benefit_ccf': benefit_ccf,
                'hr_payroll_pila_id': rec.id
            })
            rec.check_log = False
        # Load data for File 2 - Record Type 1
        if line_one:
            current_company = line_one.hr_payroll_pila_id.company_id

            register_type = '1'
            template_mode = ''
            consecutive = '1'

            company_name = line_one.company_name
            document_type = line_one.document_type
            identification_number = line_one.identification_number
            verification_code = line_one.verification_code
            template_type = 'E'
            template_ref_number = ''
            template_ref_payment_date = ''
            presentation_form = line_one.presentation_form
            sucursal_code = line_one.sucursal_code
            sucursal_name = line_one.sucursal_name

            code_arl = ''
            if current_company and current_company.arl_id.identificator_arl:
                code_arl = current_company.arl_id.identificator_arl
            else:
                message = message + _(' - ARL Company') + '\n'

            payment_period = ''
            health_payment_period = line_one.hr_payroll_pila_id.year + '-' + str(
                line_one.hr_payroll_pila_id.month).rjust(2, "0")
            template_number = ''
            payment_date = False
            total_employees = '0'
            total_payroll = '0'
            aportant_type = line_one.aportant_type
            operator_code = ''

            line_two = self.env['hr.type2f2_1.line'].create({
                'register_type': register_type,
                'template_mode': template_mode,
                'consecutive': consecutive,
                'company_name': company_name,
                'document_type': document_type,
                'identification_number': identification_number,
                'verification_code': verification_code,
                'template_type': template_type,
                'template_ref_number': template_ref_number,
                'template_ref_payment_date': template_ref_payment_date,
                'presentation_form': presentation_form,
                'sucursal_code': sucursal_code,
                'sucursal_name': sucursal_name,
                'code_arl': code_arl,
                'payment_period': payment_period,
                'health_payment_period': health_payment_period,
                'template_number': template_number,
                'payment_date': payment_date,
                'total_employees': total_employees,
                'total_payroll': total_payroll,
                'aportant_type': aportant_type,
                'operator_code': operator_code,
                'hr_payroll_pila_id': rec.id
            })

        if message != '':
            rec.check_log = True
            title = _('Review the Following Company Fields: ') + str(rec.company_id.name) + '\n\n'
            rec.log = title + message
        else:
            rec.state = 'draft'

    def action_process(self):
        for rec in self:
            rec.line2_2_ids.unlink()

            rec.check_log = False
            rec.log = ''

            day_of_week, month_days = calendar.monthrange(int(rec.year), int(rec.month))

            ini_pila = datetime.date(int(rec.year), int(rec.month), 1)
            fin_pila = datetime.date(int(rec.year), int(rec.month), month_days)

            payslip_ids = self.env['hr.payslip'].search(
                [('company_id', '=', rec.company_id.id), ('state', 'in', ('done', 'paid')),
                 ('date_from', '>=', ini_pila), ('date_to', '<=', fin_pila)])

            # Load General Line
            employees = []
            employee_ids = []
            for payslip in payslip_ids:
                if not payslip.employee_id in employee_ids:
                    employees.append(payslip.employee_id)
                    employee_ids.append(payslip.employee_id.id)

            rec.line2_1_ids.total_employees = len(employee_ids)

            # Load General Payement
            for employee in employees:
                payslip_lines = self.env['hr.payslip.line'].search(
                    [('slip_id', 'in', payslip_ids.ids), ('employee_id', '=', employee.id),
                     ('salary_rule_id.code', '=', 'M000')])

                days = 0
                ibc = 0
                for payslip_line in payslip_lines:
                    days += payslip_line.days
                    ibc += payslip_line.amount

                if days != 0:
                    line_two = rec.create_line2_2('GEN', employee, days, ibc)

            # Load Entry Novelties
            novelty_ids = self.env['hr.employee'].search(
                [('company_id', '=', rec.company_id.id), ('id', 'in', employee_ids), ('entry_date', '>=', ini_pila),
                 ('entry_date', '<=', fin_pila)])
            for novelty in novelty_ids:
                line_two = rec.create_line2_2('ING', novelty, ((fin_pila - novelty.entry_date).days + 1),
                                              start_date=novelty.entry_date)

            # Load Exit Novelties
            novelty_ids = self.env['hr.contract.completion'].search(
                [('employee_id', 'in', employee_ids), ('date', '>=', ini_pila), ('date', '<=', fin_pila),
                 ('state', '=', 'approved')])
            for novelty in novelty_ids:
                line_two = rec.create_line2_2('RET', novelty.employee_id, ((novelty.date - ini_pila).days + 1),
                                              start_date=novelty.date)

            # Load Personal Configuration Novelties
            pila_report_config = self.env['hr.pila.report.config'].search([])
            for pila_config in pila_report_config:

                event_ids = []
                for line in pila_config.line_ids:
                    event_ids.append(line.event_id.id)

                for employee in employees:

                    pv_ids = self.env['hr.pv'].search(
                        [('company_id', '=', rec.company_id.id), ('employee_id', '=', employee.id),
                         ('event_id', 'in', event_ids), ('state', 'in', ('approved', 'processed'))])

                    if pila_config.code in ('VST', 'AFP_AFI', 'AFP_APO'):
                        ibc = 0
                        for pv in pv_ids:
                            # 1. PV dentro del rango de pila
                            # 2. PV Inicia antes del inicio de Pila
                            # 2. PV Finaliza después del inicio de pila o Después del fin de pila
                            # 3. PV inicia después del inicio de pila
                            # 3. PV Finaliza después del fin de pila

                            if ((ini_pila <= pv.start_date.date()) and (fin_pila >= pv.end_date.date())) or (
                                    (ini_pila <= pv.start_date.date()) and (fin_pila < pv.end_date.date()) and (
                                    fin_pila >= pv.start_date.date())) or (
                                    (ini_pila > pv.start_date.date()) and (fin_pila >= pv.end_date.date()) and (
                                    fin_pila > pv.start_date.date()) and (ini_pila <= pv.end_date.date())) or (
                                    (ini_pila > pv.start_date.date()) and (fin_pila < pv.end_date.date())):
                                ibc += pv.amount

                                line_two = rec.create_line2_2(pila_config.code, employee, 0, ibc)
                    else:
                        for pv in pv_ids:
                            # 1. PV dentro del rango de pila
                            # 2. PV Inicia antes del inicio de Pila
                            # 2. PV Finaliza después del inicio de pila o Después del fin de pila
                            # 3. PV inicia después del inicio de pila
                            # 3. PV Finaliza después del fin de pila
                            if ((ini_pila <= pv.start_date.date()) and (fin_pila >= pv.end_date.date())) or (
                                    (ini_pila <= pv.start_date.date()) and (fin_pila < pv.end_date.date()) and (
                                    fin_pila >= pv.start_date.date())) or (
                                    (ini_pila > pv.start_date.date()) and (fin_pila >= pv.end_date.date()) and (
                                    fin_pila > pv.start_date.date()) and (ini_pila <= pv.end_date.date())) or (
                                    (ini_pila > pv.start_date.date()) and (fin_pila < pv.end_date.date())):
                                line_two = rec.create_line2_2(pila_config.code, pv.employee_id,
                                                              ((pv.end_date.date() - pv.start_date.date()).days + 1),
                                                              start_date=pv.start_date.date(),
                                                              end_date=pv.end_date.date())

            # Load EPS transfers
            eps_transfers = self.env['hr.request.for.news'].search(
                [('employee_id', 'in', employee_ids), ('start_date', '>=', ini_pila),
                 ('final_date', '<=', fin_pila),
                 ('subsystem', '=', 'eps'), ('process', '=', 'transfers'), ('state', '=', 'finalized')])

            for eps_transfer in eps_transfers:
                line_two = rec.create_line2_2('TDE', eps_transfer.employee_id, 0)

                line_two.code_eps = eps_transfer.source_entity

            # Load AFP transfers
            afp_transfers = self.env['hr.request.for.news'].search(
                [('employee_id', 'in', employee_ids), ('start_date', '>=', ini_pila),
                 ('final_date', '<=', fin_pila),
                 ('subsystem', '=', 'afp'), ('process', '=', 'transfers'), ('state', '=', 'finalized')])

            for afp_transfer in afp_transfers:
                line_two = rec.create_line2_2('TDP', afp_transfer.employee_id, 0)

                line_two.code_afp = afp_transfer.source_entity

            # Load Salary Increase
            salary_increases = self.env['hr.request.for.news'].search(
                [('employee_id', 'in', employee_ids), ('start_date', '>=', ini_pila),
                 ('final_date', '<=', fin_pila),
                 ('check_salary', '=', True), ('state', '=', 'finalized')])

            for salary_increase in salary_increases:
                line_two = rec.create_line2_2('VPS', salary_increase.employee_id, 0,
                                              start_date=salary_increase.start_date)

            rec.write({
                'check_log': rec.check_log
            })

            if not rec.check_log:
                rec.state = 'process'

    def action_done(self):
        for rec in self:
            data = ''
            data_1 = ''

            for line in rec.line1_ids:
                data += eval(rec.action_process_file(line._name, 'company_name', line.company_name, 200, 'a'))
                data += eval(rec.action_process_file(line._name, 'document_type', line.document_type, 2, 'a'))
                data += eval(
                    rec.action_process_file(line._name, 'identification_number', line.identification_number, 16, 'a'))
                data += eval(rec.action_process_file(line._name, 'verification_code', line.verification_code, 1, 'n'))
                data += eval(rec.action_process_file(line._name, 'sucursal_code', line.sucursal_code, 10, 'a'))
                data += eval(rec.action_process_file(line._name, 'sucursal_name', line.sucursal_name, 40, 'a'))
                data += eval(rec.action_process_file(line._name, 'contributor_class', line.contributor_class, 1, 'a'))
                data += eval(rec.action_process_file(line._name, 'legal_nature', line.legal_nature, 1, 'n'))
                data += eval(rec.action_process_file(line._name, 'person_type', line.person_type, 1, 'a'))
                data += eval(rec.action_process_file(line._name, 'presentation_form', line.presentation_form, 1, 'a'))
                data += eval(rec.action_process_file(line._name, 'street', line.street, 40, 'a'))
                data += eval(rec.action_process_file(line._name, 'divpola_code', line.divpola_code, 3, 'a'))
                data += eval(rec.action_process_file(line._name, 'state', line.state, 2, 'a'))
                data += eval(rec.action_process_file(line._name, 'ica_activity', line.ica_activity, 4, 'n'))
                data += eval(rec.action_process_file(line._name, 'phone', line.phone, 10, 'n'))
                data += eval(rec.action_process_file(line._name, 'mobile', line.mobile, 10, 'n'))
                data += eval(rec.action_process_file(line._name, 'email', line.email, 60, 'n'))
                data += eval(
                    rec.action_process_file(line._name, 'rl_identification_id', line.rl_identification_id, 16, 'a'))
                data += eval(
                    rec.action_process_file(line._name, 'rl_verification_code', line.rl_verification_code, 1, 'n'))
                data += eval(rec.action_process_file(line._name, 'rl_document_type', line.rl_document_type, 2, 'a'))
                data += eval(rec.action_process_file(line._name, 'rl_third_name', line.rl_third_name, 20, 'a'))
                data += eval(rec.action_process_file(line._name, 'rl_fourth_name', line.rl_fourth_name, 30, 'a'))
                data += eval(rec.action_process_file(line._name, 'rl_first_name', line.rl_first_name, 20, 'a'))
                data += eval(rec.action_process_file(line._name, 'rl_second_name', line.rl_second_name, 30, 'a'))
                data += eval(rec.action_process_file(line._name, 'concordate_date', line.concordate_date, 10, 'a'))
                data += eval(rec.action_process_file(line._name, 'action_type', line.action_type, 1, 'n'))
                data += eval(
                    rec.action_process_file(line._name, 'concordate_end_date', str(line.concordate_end_date), 10, 'a'))
                data += eval(rec.action_process_file(line._name, 'operator', line.operator, 2, 'n'))
                data += eval(rec.action_process_file(line._name, 'payment_period', line.payment_period, 7, 'n'))
                data += eval(rec.action_process_file(line._name, 'aportant_type', line.aportant_type, 2, 'n'))
                data += eval(
                    rec.action_process_file(line._name, 'commercial_register_date', str(line.commercial_register_date),
                                            10, 'a'))
                data += eval(rec.action_process_file(line._name, 'state_partner', line.state_partner, 2, 'a'))
                data += eval(rec.action_process_file(line._name, 'icbf', line.icbf, 1, 'a'))
                data += eval(rec.action_process_file(line._name, 'benefit_ccf', line.benefit_ccf, 1, 'a')) + '\n'

            for line in rec.line2_1_ids:
                data_1 += eval(rec.action_process_file(line._name, 'register_type', line.register_type, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'template_mode', line.template_mode, 1, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'consecutive', line.consecutive, 4, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'company_name', line.company_name, 200, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'document_type', line.document_type, 2, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'identification_number', line.identification_number, 16, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'verification_code', line.verification_code, 1, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'template_type', line.template_type, 1, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'template_ref_number', line.template_ref_number, 10, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'template_ref_payment_date', line.template_ref_payment_date, 10,
                                            'a'))
                data_1 += eval(rec.action_process_file(line._name, 'presentation_form', line.presentation_form, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'sucursal_code', line.sucursal_code, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'sucursal_name', line.sucursal_name, 40, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'code_arl', line.code_arl, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'payment_period', line.payment_period, 7, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'health_payment_period', line.health_payment_period, 7, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'template_number', line.template_number, 10, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'payment_date', line.payment_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'total_employees', line.total_employees, 4, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'total_payroll', line.total_payroll, 12, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'aportant_type', line.aportant_type, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'operator_code', line.operator_code, 2, 'n')) + '\n'

            rec_count = 1
            for line in sorted(rec.line2_2_ids, key=lambda lines: (
                    lines.third_name, lines.fourth_name, lines.first_name, lines.second_name)):
                data_1 += eval(rec.action_process_file(line._name, 'register_type', line.register_type, 2, 'n'))
                line.consecutive = str(int(rec_count))
                data_1 += eval(rec.action_process_file(line._name, 'consecutive', line.consecutive, 5, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'document_type', line.document_type, 2, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'identification_number', line.identification_number, 16, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'contributor_type', line.contributor_type, 2, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'contributor_subtype', line.contributor_subtype, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'is_foreign', line.is_foreign, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'colombian_abroad', line.colombian_abroad, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'state', line.state, 2, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'divpola_code', line.divpola_code, 3, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'third_name', line.third_name, 20, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'fourth_name', line.fourth_name, 30, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'first_name', line.first_name, 20, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'second_name', line.second_name, 30, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_ing', line.is_ing, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_ret', line.is_ret, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_tde', line.is_tde, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_tae', line.is_tae, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_tdp', line.is_tdp, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_tap', line.is_tap, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_vsp', line.is_vsp, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_correction', line.is_correction, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_vst', line.is_vst, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_sln', line.is_sln, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_ige', line.is_ige, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_lma', line.is_lma, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_vac_lr', line.is_vac_lr, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_avp', line.is_avp, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'is_vct', line.is_vct, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'irl_days', line.irl_days, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'code_afp', line.code_afp, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'code_new_afp', line.code_new_afp, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'code_eps', line.code_eps, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'code_new_eps', line.code_new_eps, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'code_ccf', line.code_ccf, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_days', line.pension_days, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'health_days', line.health_days, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'arl_days', line.arl_days, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'ccf_days', line.ccf_days, 2, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'salary', line.salary, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'is_integral_salary', line.is_integral_salary, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_ibc', line.pension_ibc, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'health_ibc', line.health_ibc, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'arl_ibc', line.arl_ibc, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'ccf_ibc', line.ccf_ibc, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_rate', line.pension_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_value', line.pension_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_vol_emp', line.pension_vol_emp, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_vol_com', line.pension_vol_com, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'pension_total', line.pension_total, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'solidarity_fund_sol', line.solidarity_fund_sol, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'solidarity_fund_sub', line.solidarity_fund_sub, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'total_not_retained', line.total_not_retained, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'health_rate', line.health_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'health_value', line.health_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'upc_value', line.upc_value, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'disability_number', line.disability_number, 15, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'disability_value', line.disability_value, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'maternity_disability_number', line.maternity_disability_number,
                                            15, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'maternity_disability_value', line.maternity_disability_value,
                                            9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'arl_rate', line.arl_rate, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'work_center', line.work_center, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'arl_value', line.arl_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'ccf_rate', line.ccf_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'ccf_value', line.ccf_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'sena_rate', line.sena_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'sena_value', line.sena_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'icbf_rate', line.icbf_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'icbf_value', line.icbf_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'esap_rate', line.esap_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'esap_value', line.esap_value, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'men_rate', line.men_rate, 7, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'men_value', line.men_value, 9, 'n'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'principal_document_type', line.principal_document_type, 2,
                                            'a'))
                data_1 += eval(rec.action_process_file(line._name, 'principal_identification_number',
                                                       line.principal_identification_number, 16, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'exempt_from_payment', line.exempt_from_payment, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'arl_code', line.arl_code, 6, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'risk_level', line.risk_level, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'special_pension', line.special_pension, 1, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'ing_date', line.ing_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'ret_date', line.ret_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'vsp_date', line.vsp_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'sln_initial_date', line.sln_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'sln_end_date', line.sln_end_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'ige_initial_date', line.ige_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'ige_end_date', line.ige_end_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'lma_initial_date', line.lma_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'lma_end_date', line.lma_end_date, 10, 'a'))
                data_1 += eval(
                    rec.action_process_file(line._name, 'vac_lr_initial_date', line.vac_lr_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'vac_lr_end_date', line.vac_lr_end_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'vct_initial_date', line.vct_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'vct_end_date', line.vct_end_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'irl_initial_date', line.irl_initial_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'irl_end_date', line.irl_end_date, 10, 'a'))
                data_1 += eval(rec.action_process_file(line._name, 'ibc_amount', line.ibc_amount, 9, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'workly_hours', line.workly_hours, 3, 'n'))
                data_1 += eval(rec.action_process_file(line._name, 'abroad_date', line.abroad_date, 10, 'a')) + '\n'

                rec_count += 1

            filename = str(rec.company_id.name).replace(' ', '') + '_' + \
                       str(rec.year) + '_' + str(rec.month).rjust(2, "0") + '.txt'

            rec.write({
                'file1': base64.b64encode(data.encode()),
                'file1_name': 'AT1' + '_' + filename,
                'file2': base64.b64encode(data_1.encode()),
                'file2_name': 'AT2' + '_' + filename,
                'state': 'done'})

    def create_line2_2(self, novelty_type, employee, days, amount=0, start_date=False, end_date=False):
        message = ''
        line2_2 = False

        for rec in self:

            if days > 30:
                days = 30

            create = False
            if novelty_type in ('SLN', 'IGE', 'LMA', 'VAC-LR'):
                create = True

            if not create:
                for line in rec.line2_2_ids.filtered(lambda x: x.identification_number == employee.identification_id):
                    if line.is_sln == "" and line.is_ige == "" and line.is_lma == "" and line.is_vac_lr == "":
                        line2_2 = line
                        break

                if not line2_2:
                    create = True

            if create:
                contract = self.env['hr.contract'].search(
                    [('employee_id', '=', employee.id), ('state', '=', 'open')], limit=1)

                day_of_week, month_days = calendar.monthrange(int(rec.year), int(rec.month))

                register_type = "1"
                consecutive = "1"

                document_type = ""
                if employee.partner_id._l10n_co_edi_get_carvajal_code_for_identification_type():
                    document_type = employee.partner_id._l10n_co_edi_get_carvajal_code_for_identification_type()
                else:
                    message = message + ' - ' + _('Document Type') + ' - ' + str(employee.name) + '\n'

                identification_number = ""
                if employee.identification_id:
                    identification_number = employee.identification_id
                else:
                    message = message + ' - ' + _('Identification Number') + ' - ' + str(employee.name) + '\n'

                contributor_type = ''
                if employee.contributor_type_id.code:
                    contributor_type = employee.contributor_type_id.code
                else:
                    message = message + ' - ' + _('Contributor Type') + ' - ' + str(employee.name) + '\n'

                contributor_subtype = ''
                if employee.contributor_subtype_id.code:
                    contributor_subtype = employee.contributor_subtype_id.code
                else:
                    message = message + ' - ' + _('Contributor SubType') + ' - ' + str(employee.name) + '\n'

                is_foreign = ""
                if employee.is_foreign:
                    is_foreign = "X"
                colombian_abroad = ""
                state = ""
                if employee.is_foreign:
                    state = "0"
                if employee.address_home_id and employee.address_home_id.state_id:
                    state = employee.address_home_id.state_id.code
                else:
                    message = message + ' - ' + _('State') + ' - ' + str(employee.name) + '\n'

                divpola_code = ""
                if employee.address_home_id and employee.address_home_id.city_id:
                    divpola_code = employee.address_home_id.city_id.zipcode
                else:
                    message = message + ' - ' + _('DiviPola Code') + ' - ' + str(employee.name) + '\n'

                third_name = ""
                if employee.third_name:
                    third_name = employee.third_name
                else:
                    message = message + ' - ' + _('Third Name') + ' - ' + str(employee.name) + '\n'

                fourth_name = ""
                if employee.fourth_name:
                    fourth_name = employee.fourth_name

                first_name = ""
                if employee.first_name:
                    first_name = employee.first_name
                else:
                    message = message + ' - ' + _('First Name') + ' - ' + str(employee.name) + '\n'

                second_name = ""
                if employee.second_name:
                    second_name = employee.second_name

                is_ing = ""
                is_ret = ""
                is_tde = ""
                is_tae = ""
                is_tdp = ""
                is_tap = ""
                is_vsp = ""
                is_correction = ""
                is_vst = ""
                is_sln = ""
                is_ige = ""
                is_lma = ""
                is_vac_lr = ""
                is_avp = ""
                is_vct = ""

                irl_days = days if novelty_type == 'IRL' else '0'

                code_afp = ""
                if employee.afp_partner_id and employee.afp_partner_id.identificator_afp:
                    code_afp = employee.afp_partner_id.identificator_afp
                else:
                    message = message + ' - ' + _('AFP Code') + ' - ' + str(employee.name) + '\n'

                code_new_afp = ""

                code_eps = ""
                if employee.eps_partner_id and employee.eps_partner_id.identificator_eps:
                    code_eps = employee.eps_partner_id.identificator_eps
                else:
                    message = message + ' - ' + _('EPS Code') + ' - ' + str(employee.name) + '\n'

                code_new_eps = ""

                code_ccf = ""
                if employee.ccf_partner_id and employee.ccf_partner_id.identificator_box:
                    code_ccf = employee.ccf_partner_id.identificator_box
                else:
                    message = message + ' - ' + _('CCF Code') + ' - ' + str(employee.name) + '\n'

                pension_days = days
                health_days = days
                arl_days = days
                ccf_days = days

                salary = ""
                if contract:
                    salary = str(round_up(contract.wage))

                is_integral_salary = ""
                if contract.salary_type == 'salario_integral':
                    is_integral_salary = 'X'

                if amount == 0:
                    amount = round_up((contract.wage / 30) * days)

                pension_ibc = str(round_up(amount)) if amount != 0 else '0'
                health_ibc = str(round_up(amount)) if amount != 0 else '0'
                arl_ibc = str(round_up(amount)) if amount != 0 else '0'
                ccf_ibc = str(round_up(amount)) if amount != 0 else '0'

                pension_rate = str(
                    employee.contributor_type_id.pension_rate / 100) if employee.contributor_type_id.has_afp else "0"
                pension_value = str(round_up((employee.contributor_type_id.pension_rate / 100) * float(
                    pension_ibc))) if employee.contributor_type_id.has_afp else "0"
                pension_vol_emp = "0"
                pension_vol_com = "0"
                # pension_total = "" compute field
                solidarity_fund_sol = ""
                solidarity_fund_sub = ""
                total_not_retained = ""
                health_rate = str(
                    employee.contributor_type_id.eps_rate / 100) if employee.contributor_type_id.has_eps else "0"
                health_value = str(round_up((employee.contributor_type_id.eps_rate / 100) * float(
                    health_ibc))) if employee.contributor_type_id.has_eps else "0"
                upc_value = ""

                disability_number = ""
                disability_value = "0"
                maternity_disability_number = ""
                maternity_disability_value = "0"

                arl_rate = str(contract.risk_type_id.percentage / 100) if contract.risk_type_id.percentage != 0 else "0"
                arl_value = str(round_up((contract.risk_type_id.percentage / 100) * float(
                    arl_ibc))) if contract.risk_type_id.percentage != 0 else "0"

                work_center = ""
                if contract.risk_type_id.code:
                    work_center = contract.risk_type_id.code
                else:
                    message = message + ' - ' + _('Work Center') + ' - ' + str(contract.name) + '\n'

                ccf_rate = str(
                    employee.contributor_type_id.ccf_rate / 100) if employee.contributor_type_id.has_ccf else "0"
                ccf_value = str(round_up((employee.contributor_type_id.ccf_rate / 100) * float(
                    ccf_ibc))) if employee.contributor_type_id.has_ccf else "0"

                sena_rate = str(rec.company_id.sena_rate / 100) if rec.company_id.sena else '0'
                sena_value = str(
                    round_up((rec.company_id.sena_rate / 100) * float(ccf_ibc))) if rec.company_id.sena else "0"

                icbf_rate = str(rec.company_id.icbf_rate / 100) if rec.company_id.icbf else '0'
                icbf_value = str(
                    round_up((rec.company_id.icbf_rate / 100) * float(ccf_ibc))) if rec.company_id.icbf else "0"

                esap_rate = "0"
                esap_value = "0"
                men_rate = "0"
                men_value = "0"

                principal_document_type = ""
                principal_identification_number = ""
                exempt_from_payment = ""

                arl_code = ""
                if employee.arl_partner_id.identificator_arl:
                    arl_code = employee.arl_partner_id.identificator_arl
                else:
                    message = message + ' - ' + _('ARL Code') + ' - ' + str(employee.name) + '\n'

                risk_level = ""
                if contract and contract.risk_type_id:
                    risk_level = contract.risk_type_id.code
                else:
                    message = message + ' - ' + _('Risk Level') + ' - ' + str(contract.name) + '\n'

                special_pension = ""
                ing_date = ''
                ret_date = ''
                vsp_date = ''
                sln_initial_date = ''
                sln_end_date = ''
                ige_initial_date = ''
                ige_end_date = ''
                lma_initial_date = ''
                lma_end_date = ''
                vac_lr_initial_date = ''
                vac_lr_end_date = ''
                vct_initial_date = ''
                vct_end_date = ''
                irl_initial_date = ''
                irl_end_date = ''
                ibc_amount = str(round_up(amount)) if amount != 0 else '0'
                workly_hours = str(int(days * 8))
                abroad_date = ''

                line2_2 = self.env['hr.type2f2_2.line'].create({
                    'register_type': register_type,
                    'consecutive': consecutive,
                    'document_type': document_type,
                    'identification_number': identification_number,
                    'contributor_type': contributor_type,
                    'contributor_subtype': contributor_subtype,
                    'is_foreign': is_foreign,
                    'colombian_abroad': colombian_abroad,
                    'state': state,
                    'divpola_code': divpola_code,
                    'third_name': third_name,
                    'fourth_name': fourth_name,
                    'first_name': first_name,
                    'second_name': second_name,
                    'is_ing': is_ing,
                    'is_ret': is_ret,
                    'is_tde': is_tde,
                    'is_tae': is_tae,
                    'is_tdp': is_tdp,
                    'is_tap': is_tap,
                    'is_vsp': is_vsp,
                    'is_correction': is_correction,
                    'is_vst': is_vst,
                    'is_sln': is_sln,
                    'is_ige': is_ige,
                    'is_lma': is_lma,
                    'is_vac_lr': is_vac_lr,
                    'is_avp': is_avp,
                    'is_vct': is_vct,
                    'irl_days': irl_days,
                    'code_afp': code_afp,
                    'code_new_afp': code_new_afp,
                    'code_eps': code_eps,
                    'code_new_eps': code_new_eps,
                    'code_ccf': code_ccf,
                    'pension_days': pension_days,
                    'health_days': health_days,
                    'arl_days': arl_days,
                    'ccf_days': ccf_days,
                    'salary': salary,
                    'is_integral_salary': is_integral_salary,
                    'pension_ibc': pension_ibc,
                    'health_ibc': health_ibc,
                    'arl_ibc': arl_ibc,
                    'ccf_ibc': ccf_ibc,
                    'pension_rate': pension_rate,
                    'pension_value': pension_value,
                    'pension_vol_emp': pension_vol_emp,
                    'pension_vol_com': pension_vol_com,
                    'solidarity_fund_sol': solidarity_fund_sol,
                    'solidarity_fund_sub': solidarity_fund_sub,
                    'total_not_retained': total_not_retained,
                    'health_rate': health_rate,
                    'health_value': health_value,
                    'upc_value': upc_value,
                    'disability_number': disability_number,
                    'disability_value': disability_value,
                    'maternity_disability_number': maternity_disability_number,
                    'maternity_disability_value': maternity_disability_value,
                    'arl_rate': arl_rate,
                    'work_center': work_center,
                    'arl_value': arl_value,
                    'ccf_rate': ccf_rate,
                    'ccf_value': ccf_value,
                    'sena_rate': sena_rate,
                    'sena_value': sena_value,
                    'icbf_rate': icbf_rate,
                    'icbf_value': icbf_value,
                    'esap_rate': esap_rate,
                    'esap_value': esap_value,
                    'men_rate': men_rate,
                    'men_value': men_value,
                    'principal_document_type': principal_document_type,
                    'principal_identification_number': principal_identification_number,
                    'exempt_from_payment': exempt_from_payment,
                    'arl_code': arl_code,
                    'risk_level': risk_level,
                    'special_pension': special_pension,
                    'ing_date': ing_date,
                    'ret_date': ret_date,
                    'vsp_date': vsp_date,
                    'sln_initial_date': sln_initial_date,
                    'sln_end_date': sln_end_date,
                    'ige_initial_date': ige_initial_date,
                    'ige_end_date': ige_end_date,
                    'lma_initial_date': lma_initial_date,
                    'lma_end_date': lma_end_date,
                    'vac_lr_initial_date': vac_lr_initial_date,
                    'vac_lr_end_date': vac_lr_end_date,
                    'vct_initial_date': vct_initial_date,
                    'vct_end_date': vct_end_date,
                    'irl_initial_date': irl_initial_date,
                    'irl_end_date': irl_end_date,
                    'ibc_amount': ibc_amount,
                    'workly_hours': workly_hours,
                    'abroad_date': abroad_date,
                    'hr_payroll_pila_id': rec.id
                })

            if message != '':
                rec.check_log = True
                title = _('\nReview the Following Employee Fields: ') + str(employee.name) + ' - ' + str(
                    employee.identification_id) + _(' and the Contract: ') + str(contract.name) + '\n\n'
                rec.log = rec.log + title + message

            if line2_2:
                if novelty_type == 'ING':
                    line2_2.is_ing = 'X'
                    line2_2.ing_date = start_date.strftime('%Y-%m-%d')

                if novelty_type == 'RET':
                    line2_2.is_ret = 'X'
                    line2_2.ret_date = start_date.strftime('%Y-%m-%d')

                if novelty_type == 'TDE':
                    line2_2.is_tde = 'X'

                if novelty_type == 'TDP':
                    line2_2.is_tdp = 'X'

                if novelty_type == 'VSP':
                    line2_2.is_vsp = 'X'
                    line2_2.vsp_date = start_date.strftime('%Y-%m-%d')

                if novelty_type == 'AFP_AFI':
                    line2_2.pension_vol_emp = str(round_up(amount))

                if novelty_type == 'AFP_APO':
                    line2_2.pension_vol_com = str(round_up(amount))

                if novelty_type == 'VST':
                    line2_2.is_vst = 'X'

                    line2_2.pension_ibc = str(round_up(float(line2_2.pension_ibc) + amount))
                    line2_2.health_ibc = str(round_up(float(line2_2.health_ibc) + amount))
                    line2_2.arl_ibc = str(round_up(float(line2_2.arl_ibc) + amount))
                    line2_2.ccf_ibc = str(round_up(float(line2_2.ccf_ibc) + amount))

                    line2_2.pension_value = str(round_up(float(line2_2.pension_ibc) * float(line2_2.pension_rate)))
                    line2_2.health_value = str(round_up(float(line2_2.health_ibc) * float(line2_2.health_rate)))
                    line2_2.arl_value = str(round_up(float(line2_2.arl_ibc) * float(line2_2.arl_rate)))
                    line2_2.ccf_value = str(round_up(float(line2_2.ccf_ibc) * float(line2_2.ccf_rate)))
                    line2_2.sena_value = str(round_up(float(line2_2.ccf_ibc) * float(line2_2.sena_rate)))
                    line2_2.icbf_value = str(round_up(float(line2_2.ccf_ibc) * float(line2_2.icbf_rate)))

                if novelty_type == 'SLN':
                    line2_2.is_sln = 'X'
                    line2_2.sln_initial_date = start_date.strftime('%Y-%m-%d')
                    line2_2.sln_end_date = end_date.strftime('%Y-%m-%d')

                if novelty_type == 'IGE':
                    line2_2.is_ige = 'X'
                    line2_2.ige_initial_date = start_date.strftime('%Y-%m-%d')
                    line2_2.ige_end_date = end_date.strftime('%Y-%m-%d')

                if novelty_type == 'LMA':
                    line2_2.is_lma = 'X'
                    line2_2.lma_initial_date = start_date.strftime('%Y-%m-%d')
                    line2_2.lma_end_date = end_date.strftime('%Y-%m-%d')

                if novelty_type == 'VAC_LR':
                    line2_2.is_vac_lr = 'X'
                    line2_2.vac_lr_initial_date = start_date.strftime('%Y-%m-%d')
                    line2_2.vac_lr_end_date = end_date.strftime('%Y-%m-%d')

            return line2_2

    def action_generate_report(self):
        for rec in self:

            rec.action_draft()
            if rec.check_log:
                break

            rec.action_process()
            if rec.check_log:
                break

            rec.action_done()

    @api.model
    def action_process_file(self, model=False, field=False, value=False, size=False, type=False):
        if field and field[-5:] == '_date' and not value:
            return 'str(line.dummy_field)' + '.ljust(' + str(size) + ')[:' + str(size) + ']'

        if value:
            hr_reports_config_line_rec = self.env['hr.reports.config.line'].search(
                [('hr_reports_config_id.name', '=', model), ('name', '=', field)], limit=1)
            if hr_reports_config_line_rec and hr_reports_config_line_rec.data_type and hr_reports_config_line_rec.size:

                if hr_reports_config_line_rec.data_type in ['alphabetic', 'boolean']:
                    return 'line.' + field + '.ljust(' + str(hr_reports_config_line_rec.size) + ')[:' + str(
                        hr_reports_config_line_rec.size) + ']'

                if hr_reports_config_line_rec.data_type in ['numeric']:
                    return 'line.' + field + '.rjust(' + str(hr_reports_config_line_rec.size) + ', "0")[:' + str(
                        hr_reports_config_line_rec.size) + ']'

                if hr_reports_config_line_rec.data_type in ['date'] and hr_reports_config_line_rec.data_format:
                    value = str(value)
                    date = datetime.datetime.strptime(value, DF)
                    date_format = datetime.date.strftime(date, hr_reports_config_line_rec.data_format)
                    return '"' + date_format + '"' + '.ljust(' + str(hr_reports_config_line_rec.size) + ')[:' + str(
                        hr_reports_config_line_rec.size) + ']'

            if not hr_reports_config_line_rec:
                if field and field[-5:] == '_date':
                    field = 'str(line.' + field + ')'
                    if type == 'a':
                        return field + '.ljust(' + str(size) + ')[:' + str(size) + ']'
                    if type == 'n':
                        return field + '.rjust(' + str(size) + ', "0")[:' + str(size) + ']'

                if type == 'a':
                    return 'line.' + field + '.ljust(' + str(size) + ')[:' + str(size) + ']'

                if type == 'n':
                    return 'line.' + field + '.rjust(' + str(size) + ', "0")[:' + str(size) + ']'

        if not value and size and type:
            if field and field[-5:] == '_date':
                field = 'str(' + field + ')'
                if type == 'a':
                    return field + '.ljust(' + str(size) + ')[:' + str(size) + ']'
                if type == 'n':
                    return field + '.rjust(' + str(size) + ', "0")[:' + str(size) + ']'

            if type == 'a':
                return 'line.' + field + '.ljust(' + str(size) + ')[:' + str(size) + ']'

            if type == 'n':
                return 'line.' + field + '.rjust(' + str(size) + ', "0")[:' + str(size) + ']'

    def print_xlsx(self):

        lines = []
        for line in self.line2_2_ids:
            data = {
                'register_type': line.register_type,
                'consecutive': line.consecutive,
                'document_type': line.document_type,
                'identification_number': line.identification_number,
                'contributor_type': line.contributor_type,
                'contributor_subtype': line.contributor_subtype,
                'is_foreign': line.is_foreign,
                'colombian_abroad': line.colombian_abroad,
                'state': line.state,
                'divpola_code': line.divpola_code,
                'third_name': line.third_name,
                'fourth_name': line.third_name,
                'first_name': line.first_name,
                'second_name': line.second_name,
                'is_ing': line.is_ing,
                'is_ret': line.is_ret,
                'is_tde': line.is_tde,
                'is_tae': line.is_tae,
                'is_tdp': line.is_tdp,
                'is_tap': line.is_tap,
                'is_vsp': line.is_vsp,
                'is_correction': line.is_correction,
                'is_vst': line.is_vst,
                'is_sln': line.is_sln,
                'is_ige': line.is_ige,
                'is_lma': line.is_lma,
                'is_vac_lr': line.is_vac_lr,
                'is_avp': line.is_avp,
                'is_vct': line.is_vct,
                'irl_days': line.irl_days,
                'code_afp': line.code_afp,
                'code_new_afp': line.code_new_afp,
                'code_eps': line.code_eps,
                'code_new_eps': line.code_new_eps,
                'code_ccf': line.code_ccf,
                'pension_days': line.pension_days,
                'health_days': line.health_days,
                'arl_days': line.arl_days,
                'ccf_days': line.ccf_days,
                'salary': float(line.salary),
                'is_integral_salary': line.is_integral_salary,
                'pension_ibc': float(line.pension_ibc),
                'health_ibc': float(line.health_ibc),
                'arl_ibc': float(line.arl_ibc),
                'ccf_ibc': float(line.ccf_ibc),
                'pension_rate': float(line.pension_rate),
                'pension_value': float(line.pension_value),
                'pension_vol_emp': float(line.pension_vol_emp),
                'pension_vol_com': float(line.pension_vol_com),
                'pension_total': float(line.pension_total),
                'solidarity_fund_sol': line.solidarity_fund_sol,
                'solidarity_fund_sub': line.solidarity_fund_sub,
                'total_not_retained': line.total_not_retained,
                'health_rate': line.health_rate,
                'health_value': float(line.health_value),
                'upc_value': line.upc_value,
                'disability_number': line.disability_number,
                'disability_value': line.disability_value,
                'maternity_disability_number': line.maternity_disability_number,
                'maternity_disability_value': line.maternity_disability_value,
                'arl_rate': line.arl_rate,
                'work_center': line.work_center,
                'arl_value': float(line.arl_value),
                'ccf_rate': line.ccf_rate,
                'ccf_value': float(line.ccf_value),
                'sena_rate': line.sena_rate,
                'sena_value': float(line.sena_value),
                'icbf_rate': line.icbf_rate,
                'icbf_value': float(line.icbf_value),
                'esap_rate': line.esap_rate,
                'esap_value': float(line.esap_value),
                'men_rate': line.men_rate,
                'men_value': float(line.men_value),
                'principal_document_type': line.principal_document_type,
                'principal_identification_number': line.principal_identification_number,
                'exempt_from_payment': line.exempt_from_payment,
                'arl_code': line.arl_code,
                'risk_level': line.risk_level,
                'special_pension': line.special_pension,
                'ing_date': line.ing_date,
                'ret_date': line.ret_date,
                'vsp_date': line.vsp_date,
                'sln_initial_date': line.sln_initial_date,
                'sln_end_date': line.sln_end_date,
                'ige_initial_date': line.ige_initial_date,
                'ige_end_date': line.ige_initial_date,
                'lma_initial_date': line.lma_initial_date,
                'lma_end_date': line.lma_end_date,
                'vac_lr_initial_date': line.vac_lr_initial_date,
                'vac_lr_end_date': line.vac_lr_end_date,
                'vct_initial_date': line.vct_initial_date,
                'vct_end_date': line.vct_end_date,
                'irl_initial_date': line.irl_initial_date,
                'irl_end_date': line.irl_end_date,
                'ibc_amount': float(line.ibc_amount),
                'workly_hours': float(line.workly_hours),
                'abroad_date': line.abroad_date,
            }

            lines.append(data)

        data = {
            'partners': lines,
        }

        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'hr.payroll.pila',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'pila/' + str(date.today().strftime("%d-%m-%y")),
                     }
        }

    def get_xlsx_report(self, data, response):

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'bold': False,
                                           'text_wrap': True,
                                           'valign': 'top',
                                           'bg_color': '#A9A9A9',
                                           'border': 1})
        format_num_char = workbook.add_format({'num_format': '@'})
        money = workbook.add_format({'num_format': '$#,##0'})

        sheet.set_column(0, 96, 30)  # Width of columns B:D set to 30.
        sheet.set_row(row=0, height=30)

        sheet.write('A1', 'Tipo de Registro', cell_format)
        sheet.write('B1', 'Sec.identif.registro', cell_format)
        sheet.write_string('C1', 'Tipo de documento del cotizante', cell_format)
        sheet.write_string('D1', 'Número de identificación del cotizante', cell_format)
        sheet.write_string('E1', 'Tipo cotizante', cell_format)
        sheet.write_string('F1', 'Subtipo de cotizante', cell_format)
        sheet.write('G1', 'Extranjero no obligado a cotizar pensión', cell_format)
        sheet.write('H1', 'Colombiano residente en el exterior', cell_format)
        sheet.write('I1', 'Departamento de ubicación laboral', cell_format)
        sheet.write('J1', 'ID Ciudad', cell_format)
        sheet.write('K1', 'Apellido', cell_format)
        sheet.write('L1', 'Segundo apellido', cell_format)
        sheet.write('M1', 'Primer Nombre', cell_format)
        sheet.write('N1', 'Segundo Nombre', cell_format)
        sheet.write('O1', 'Indicador: Novedad de Ingreso', cell_format)
        sheet.write('P1', 'Indicador: Novedad de Retiro', cell_format)
        sheet.write('Q1', 'Novedad TDE', cell_format)
        sheet.write('R1', 'Novedad TAE', cell_format)
        sheet.write('S1', 'Novedad TDP', cell_format)
        sheet.write('T1', 'Novedad TAP', cell_format)
        sheet.write('U1', 'Novedad VSP', cell_format)
        sheet.write('V1', 'Indicador de planilla de correcciones', cell_format)
        sheet.write('W1', 'Novedad VST', cell_format)
        sheet.write('X1', 'Susp. temporaria/licencia no remunerada', cell_format)
        sheet.write('Y1', 'Novedad IGE', cell_format)
        sheet.write('Z1', 'Novedad LMA', cell_format)
        sheet.write('AA1', 'Vacaciones/Licencia Remunerada', cell_format)
        sheet.write('AB1', 'Novedad AVP', cell_format)
        sheet.write('AC1', 'Novedad VCT', cell_format)
        sheet.write('AD1', 'Días Novedad IRP', cell_format)
        sheet.write('AE1', 'ID Entidad AFP', cell_format)
        sheet.write('AF1', 'ID Nueva Entidad AFP', cell_format)
        sheet.write('AG1', 'ID Entidad EPS', cell_format)
        sheet.write('AH1', 'ID Nueva Entidad EPS', cell_format)
        sheet.write('AI1', 'ID Entidad CAJA', cell_format)
        sheet.write('AJ1', 'No. Días Cotizados AFP', cell_format)
        sheet.write('AK1', 'No. Días Cotizados EPS', cell_format)
        sheet.write('AL1', 'Días Cotizados a Riesgos Profesionales', cell_format)
        sheet.write('AM1', 'No. Días Cotizados CCF', cell_format)
        sheet.write('AN1', 'Sueldo Empleado', cell_format)
        sheet.write('AO1', 'Salario Integral', cell_format)
        sheet.write('AP1', 'Ingreso Base Cotización Pensión', cell_format)
        sheet.write('AQ1', 'Ingreso Base Cotización Salud', cell_format)
        sheet.write('AR1', 'IBC Riesgos Laborales', cell_format)
        sheet.write('AS1', 'IBC Caja Compensación Familiar', cell_format)
        sheet.write('AT1', 'Porcentaje AFP', cell_format)
        sheet.write('AU1', 'Valor aporte Pensión', cell_format)
        sheet.write('AV1', 'Aporte Voluntario Empleado', cell_format)
        sheet.write('AW1', 'Aporte Voluntario Empleador', cell_format)
        sheet.write('AX1', 'Aporte Total', cell_format)
        sheet.write('AY1', 'FSP Subcta.Solidaridad', cell_format)
        sheet.write('AZ1', 'FSP Subcta.Subsitencia', cell_format)
        sheet.write('BA1', 'Valores No Retenidos', cell_format)
        sheet.write('BB1', 'Porcentaje EPS', cell_format)
        sheet.write('BC1', 'Valor aporte Salud', cell_format)
        sheet.write('BD1', 'Valor del UPC', cell_format)
        sheet.write('BE1', 'Número de Aprobación IGE', cell_format)
        sheet.write('BF1', 'Valor Incapacidades IGE', cell_format)
        sheet.write('BG1', 'Número de Aprobación LMA', cell_format)
        sheet.write('BH1', 'Valor Lic.Maternidad', cell_format)
        sheet.write('BI1', 'Porcentaje ARL', cell_format)
        sheet.write('BJ1', 'Centro de Trabajo', cell_format)
        sheet.write('BK1', 'Valor aporte Riesgos Profesionales', cell_format)
        sheet.write('BL1', 'Porcentaje CAJA de Compensacción', cell_format)
        sheet.write('BM1', 'Vr. Aporte CAJA', cell_format)
        sheet.write('BN1', 'Porcentaje SENA', cell_format)
        sheet.write('BO1', 'Vr. Aporte SENA', cell_format)
        sheet.write('BP1', 'Porcentaje ICBF', cell_format)
        sheet.write('BQ1', 'Vr. Aporte ICBF', cell_format)
        sheet.write('BR1', 'Porcentaje ESAP', cell_format)
        sheet.write('BS1', 'Vr. Aporte ESAP', cell_format)
        sheet.write('BT1', 'Porcentaje MINEDUCACIÓN', cell_format)
        sheet.write('BU1', 'Vr. Aporte Ministerio de Educación', cell_format)
        sheet.write('BV1', 'Tipo de documento cotizante principal', cell_format)
        sheet.write('BW1', 'Número de identificación del cotizante', cell_format)
        sheet.write('BX1', 'No paga aportes (salud, sena, icbf)', cell_format)
        sheet.write('BY1', 'ID Entidad ARL', cell_format)
        sheet.write('BZ1', 'Clase de riesgo', cell_format)
        sheet.write('CA1', 'Indicador: Tarifa especial de pensiones', cell_format)
        sheet.write('CB1', 'Fecha de ingreso', cell_format)
        sheet.write('CC1', 'Fecha de retiro', cell_format)
        sheet.write('CD1', 'Inicio variación permanente de salario', cell_format)
        sheet.write('CE1', 'Fecha de inicio de suspensión temporaria', cell_format)
        sheet.write('CF1', 'Fecha de fin de suspensión temporaria', cell_format)
        sheet.write('CG1', 'Fecha de inicio de incapacidad general', cell_format)
        sheet.write('CH1', 'Fecha de fin de incapacidad general', cell_format)
        sheet.write('CI1', 'Fecha de inicio de licencia maternidad', cell_format)
        sheet.write('CJ1', 'Fecha de fin de licencia maternidad', cell_format)
        sheet.write('CK1', 'Fecha de inicio de vacaciones', cell_format)
        sheet.write('CL1', 'Fecha de fin de vacaciones', cell_format)
        sheet.write('CM1', 'Fecha inicio de variación centro trabajo', cell_format)
        sheet.write('CN1', 'Fecha fin de variación centro trabajo', cell_format)
        sheet.write('CO1', 'Fecha de inicio de incapacidad IRL', cell_format)
        sheet.write('CP1', 'Fecha de final de incapacidad IRL', cell_format)
        sheet.write('CQ1', 'IBC otros parafiscales diferentes a CCF', cell_format)
        sheet.write('CR1', 'Número de horas laboradas', cell_format)
        sheet.write('CS1', 'Fecha de Radicación en el Exterior', cell_format)
        sheet.write('CT1', 'Moneda', cell_format)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0

        # Iterate over the data and write it out row by row.
        for item in data['partners']:
            sheet.write(row, col, item['register_type'])
            sheet.write(row, col + 1, item['consecutive'], format_num_char)
            sheet.write(row, col + 2, item['document_type'], format_num_char)
            sheet.write(row, col + 3, item['identification_number'], format_num_char)
            sheet.write(row, col + 4, item['contributor_type'], format_num_char)
            sheet.write(row, col + 5, item['contributor_subtype'], format_num_char)
            sheet.write(row, col + 6, item['is_foreign'], format_num_char)
            sheet.write(row, col + 7, item['colombian_abroad'], format_num_char)
            sheet.write(row, col + 8, item['state'], format_num_char)
            sheet.write(row, col + 9, item['divpola_code'], format_num_char)
            sheet.write(row, col + 10, item['third_name'], format_num_char)
            sheet.write(row, col + 11, item['fourth_name'], format_num_char)
            sheet.write(row, col + 12, item['first_name'], format_num_char)
            sheet.write(row, col + 13, item['second_name'], format_num_char)
            sheet.write(row, col + 14, item['is_ing'], format_num_char)
            sheet.write(row, col + 15, item['is_ret'], format_num_char)
            sheet.write(row, col + 16, item['is_tde'], format_num_char)
            sheet.write(row, col + 17, item['is_tae'], format_num_char)
            sheet.write(row, col + 18, item['is_tdp'], format_num_char)
            sheet.write(row, col + 19, item['is_tap'], format_num_char)
            sheet.write(row, col + 20, item['is_vsp'], format_num_char)
            sheet.write(row, col + 21, item['is_correction'], format_num_char)
            sheet.write(row, col + 22, item['is_vst'], format_num_char)
            sheet.write(row, col + 23, item['is_sln'], format_num_char)
            sheet.write(row, col + 24, item['is_ige'], format_num_char)
            sheet.write(row, col + 25, item['is_lma'], format_num_char)
            sheet.write(row, col + 26, item['is_vac_lr'], format_num_char)
            sheet.write(row, col + 27, item['is_avp'], format_num_char)
            sheet.write(row, col + 28, item['is_vct'], format_num_char)
            sheet.write(row, col + 29, item['irl_days'], format_num_char)
            sheet.write(row, col + 30, item['code_afp'], format_num_char)
            sheet.write(row, col + 31, item['code_new_afp'], format_num_char)
            sheet.write(row, col + 32, item['code_eps'], format_num_char)
            sheet.write(row, col + 32, item['code_new_eps'], format_num_char)
            sheet.write(row, col + 33, item['code_ccf'])
            sheet.write(row, col + 35, item['pension_days'])
            sheet.write(row, col + 36, item['health_days'])
            sheet.write(row, col + 37, item['arl_days'])
            sheet.write(row, col + 38, item['ccf_days'])
            sheet.write(row, col + 39, item['salary'], money)
            sheet.write(row, col + 40, item['is_integral_salary'], )
            sheet.write(row, col + 41, item['pension_ibc'], money)
            sheet.write(row, col + 42, item['health_ibc'], money)
            sheet.write(row, col + 43, item['arl_ibc'], money)
            sheet.write(row, col + 44, item['ccf_ibc'], money)
            sheet.write(row, col + 45, item['pension_rate'], )
            sheet.write(row, col + 46, item['pension_value'], money)
            sheet.write(row, col + 47, item['pension_vol_emp'], money)
            sheet.write(row, col + 48, item['pension_vol_com'], money)
            sheet.write(row, col + 49, item['pension_total'], money)
            sheet.write(row, col + 50, item['solidarity_fund_sol'], money)
            sheet.write(row, col + 51, item['solidarity_fund_sub'], money)
            sheet.write(row, col + 52, item['total_not_retained'], money)
            sheet.write(row, col + 53, item['health_rate'], )
            sheet.write(row, col + 54, item['health_value'], money)
            sheet.write(row, col + 55, item['upc_value'], money)
            sheet.write(row, col + 56, item['disability_number'], )
            sheet.write(row, col + 57, item['disability_value'], )
            sheet.write(row, col + 58, item['maternity_disability_number'], )
            sheet.write(row, col + 59, item['maternity_disability_value'], )
            sheet.write(row, col + 60, item['arl_rate'], )
            sheet.write(row, col + 61, item['work_center'], )
            sheet.write(row, col + 62, item['arl_value'], money)
            sheet.write(row, col + 63, item['ccf_rate'], )
            sheet.write(row, col + 64, item['ccf_value'], money)
            sheet.write(row, col + 65, item['sena_rate'], )
            sheet.write(row, col + 66, item['sena_value'], money)
            sheet.write(row, col + 67, item['icbf_rate'], )
            sheet.write(row, col + 68, item['icbf_value'], money)
            sheet.write(row, col + 69, item['men_rate'], )
            sheet.write(row, col + 70, item['men_value'], )
            sheet.write(row, col + 71, '', )
            sheet.write(row, col + 72, '', )
            sheet.write(row, col + 73, item['principal_document_type'], )
            sheet.write(row, col + 74, item['principal_identification_number'], )
            sheet.write(row, col + 75, item['exempt_from_payment'], )
            sheet.write(row, col + 76, item['arl_code'], )
            sheet.write(row, col + 77, item['risk_level'], )
            sheet.write(row, col + 78, item['special_pension'], )
            sheet.write(row, col + 79, item['ing_date'], )
            sheet.write(row, col + 80, item['ret_date'], )
            sheet.write(row, col + 81, item['vsp_date'], )
            sheet.write(row, col + 82, item['sln_initial_date'], )
            sheet.write(row, col + 83, item['sln_end_date'], )
            sheet.write(row, col + 84, item['ige_initial_date'], )
            sheet.write(row, col + 85, item['ige_end_date'], )
            sheet.write(row, col + 86, item['lma_initial_date'], )
            sheet.write(row, col + 87, item['lma_end_date'], )
            sheet.write(row, col + 88, item['vac_lr_initial_date'], )
            sheet.write(row, col + 89, item['vac_lr_end_date'], )
            sheet.write(row, col + 90, item['vct_initial_date'], )
            sheet.write(row, col + 91, item['vct_end_date'], )
            sheet.write(row, col + 92, item['irl_initial_date'], )
            sheet.write(row, col + 93, item['irl_end_date'], )
            sheet.write(row, col + 94, item['ibc_amount'], money)
            sheet.write(row, col + 95, item['workly_hours'], )
            sheet.write(row, col + 96, item['abroad_date'], )

            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()


class HrType2f1Line(models.Model):
    """Hr Type2f1 Line."""
    _name = "hr.type2f1.line"

    hr_payroll_pila_id = fields.Many2one('hr.payroll.pila')
    company_name = fields.Char()
    document_type = fields.Char()
    identification_number = fields.Char()
    verification_code = fields.Char()
    sucursal_code = fields.Char()
    sucursal_name = fields.Char()
    contributor_class = fields.Char()
    legal_nature = fields.Char()
    person_type = fields.Char()
    presentation_form = fields.Char(default='U')
    street = fields.Char()
    divpola_code = fields.Char()
    state = fields.Char()
    ica_activity = fields.Char()
    phone = fields.Char()
    mobile = fields.Char()
    email = fields.Char()
    rl_identification_id = fields.Char()
    rl_verification_code = fields.Char(default='0')
    rl_document_type = fields.Char()
    rl_third_name = fields.Char()
    rl_fourth_name = fields.Char()
    rl_first_name = fields.Char()
    rl_second_name = fields.Char()
    concordate_date = fields.Char()
    action_type = fields.Char()
    concordate_end_date = fields.Char()
    operator = fields.Char()
    payment_period = fields.Char()
    aportant_type = fields.Char()
    commercial_register_date = fields.Char()
    state_partner = fields.Char()
    icbf = fields.Char()
    benefit_ccf = fields.Char()
    dummy_field = fields.Char(default=' ')


class HrType2f2_1Line(models.Model):
    """Hr Type2f2_1 Line."""
    _name = "hr.type2f2_1.line"

    hr_payroll_pila_id = fields.Many2one('hr.payroll.pila')
    register_type = fields.Char(default='1')
    template_mode = fields.Char()
    consecutive = fields.Char(default='1')
    company_name = fields.Char()
    document_type = fields.Char()
    identification_number = fields.Char()
    verification_code = fields.Char()
    template_type = fields.Char(default='E')
    template_ref_number = fields.Char()
    template_ref_payment_date = fields.Char()
    presentation_form = fields.Char()
    sucursal_code = fields.Char()
    sucursal_name = fields.Char()
    code_arl = fields.Char()
    payment_period = fields.Char()
    health_payment_period = fields.Char()
    template_number = fields.Char()
    payment_date = fields.Date()
    total_employees = fields.Char(default='0')
    total_payroll = fields.Char(default='0')
    aportant_type = fields.Char()
    operator_code = fields.Char()
    dummy_field = fields.Char(default=' ')


class HrType2f2_2Line(models.Model):
    """Hr Type2f2_2 Line."""
    _name = "hr.type2f2_2.line"

    @api.depends('pension_vol_emp', 'pension_vol_com', 'pension_value')
    def _calculate_pension_total(self):
        for rec in self:
            pension_total = '0'
            if rec.pension_vol_emp and rec.pension_vol_com and rec.pension_value:
                pension_total = str(round_up(float(
                    rec.pension_value) + float(rec.pension_vol_com) + float(rec.pension_vol_emp)))
            rec.pension_total = pension_total

    hr_payroll_pila_id = fields.Many2one('hr.payroll.pila')
    register_type = fields.Char()
    consecutive = fields.Char()
    document_type = fields.Char()
    identification_number = fields.Char()
    contributor_type = fields.Char()
    contributor_subtype = fields.Char()
    is_foreign = fields.Char()
    colombian_abroad = fields.Char()
    state = fields.Char()
    divpola_code = fields.Char()
    third_name = fields.Char()
    fourth_name = fields.Char()
    first_name = fields.Char()
    second_name = fields.Char()
    is_ing = fields.Char()
    is_ret = fields.Char()
    is_tde = fields.Char()
    is_tae = fields.Char()
    is_tdp = fields.Char()
    is_tap = fields.Char()
    is_vsp = fields.Char()
    is_correction = fields.Char()
    is_vst = fields.Char()
    is_sln = fields.Char()
    is_ige = fields.Char()
    is_lma = fields.Char()
    is_vac_lr = fields.Char()
    is_avp = fields.Char()
    is_vct = fields.Char()
    irl_days = fields.Char()
    code_afp = fields.Char()
    code_new_afp = fields.Char()
    code_eps = fields.Char()
    code_new_eps = fields.Char()
    code_ccf = fields.Char()
    pension_days = fields.Char()
    health_days = fields.Char()
    arl_days = fields.Char()
    ccf_days = fields.Char()
    salary = fields.Char()
    is_integral_salary = fields.Char()
    pension_ibc = fields.Char()
    health_ibc = fields.Char()
    arl_ibc = fields.Char()
    ccf_ibc = fields.Char()
    pension_rate = fields.Char()
    pension_value = fields.Char()
    pension_vol_emp = fields.Char()
    pension_vol_com = fields.Char()
    pension_total = fields.Char(compute='_calculate_pension_total')
    solidarity_fund_sol = fields.Char()
    solidarity_fund_sub = fields.Char()
    total_not_retained = fields.Char()
    health_rate = fields.Char()
    health_value = fields.Char()
    upc_value = fields.Char()
    disability_number = fields.Char()
    disability_value = fields.Char()
    maternity_disability_number = fields.Char()
    maternity_disability_value = fields.Char()
    arl_rate = fields.Char()
    work_center = fields.Char()
    arl_value = fields.Char()
    ccf_rate = fields.Char()
    ccf_value = fields.Char()
    sena_rate = fields.Char()
    sena_value = fields.Char()
    icbf_rate = fields.Char()
    icbf_value = fields.Char()
    esap_rate = fields.Char()
    esap_value = fields.Char()
    men_rate = fields.Char()
    men_value = fields.Char()
    principal_document_type = fields.Char()
    principal_identification_number = fields.Char()
    exempt_from_payment = fields.Char()
    arl_code = fields.Char()
    risk_level = fields.Char()
    special_pension = fields.Char()
    ing_date = fields.Char()
    ret_date = fields.Char()
    vsp_date = fields.Char()
    sln_initial_date = fields.Char()
    sln_end_date = fields.Char()
    ige_initial_date = fields.Char()
    ige_end_date = fields.Char()
    lma_initial_date = fields.Char()
    lma_end_date = fields.Char()
    vac_lr_initial_date = fields.Char()
    vac_lr_end_date = fields.Char()
    vct_initial_date = fields.Char()
    vct_end_date = fields.Char()
    irl_initial_date = fields.Char()
    irl_end_date = fields.Char()
    ibc_amount = fields.Char()
    workly_hours = fields.Char()
    abroad_date = fields.Char()
    dummy_field = fields.Char(default=' ')
