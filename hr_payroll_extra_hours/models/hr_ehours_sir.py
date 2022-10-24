import xlrd
import base64
import time
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEhoursSir(models.Model):
    """Hr Eehours Sir."""

    _name = "hr.ehours.sir"
    _description = "Module to load and store SIR File Group."
    _rec_name = 'create_uid'

    @api.model
    def default_get(self, fields):
        """Month and Year will fill automatic."""
        rec = super(HrEhoursSir, self).default_get(fields)
        rec.update({
            'name': time.strftime("%m-%Y")})
        return rec

    name = fields.Char("Month and Time", readonly="1")
    file = fields.Binary()
    hr_ehours_sir_line_ids = fields.One2many(
        'hr.ehours.sir.line', 'hr_ehours_sir_id')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Approved'),
         ('cancelled', 'Cancelled')],
        string='Status', default='draft')
    created_on = fields.Date()
    message = fields.Char()
    company_id = fields.Many2one(
        'res.company', string='COMPANY',
        default=lambda self: self.env.company)

    def action_approved(self):
        """Move to Approved."""
        for rec in self:
            rec.state = 'approved'

    def action_cancelled(self):
        """Move to Cancelled."""
        for rec in self:
            rec.state = 'cancelled'

    def upload_data(self):
        """Upload data from Excel."""
        for rec in self:
            if self.search_count([
                ('state', '=', 'approved'),
                ('name', '=', rec.name)]) >= 1:
                raise ValidationError(_(
                    "This month and year record is already exist."))
            if rec.file:
                workbook = xlrd.open_workbook(
                    file_contents=base64.decodestring(
                        rec.file))
                row_list = []
                last_sheet = workbook.sheet_by_index(-1)
                # Will pick last sheet of the Excel Workbook
                for row in range(2, last_sheet.nrows):
                    row_list.append(last_sheet.row_values(row))
                for line_list in row_list:
                    existing_rec = False
                    if line_list[0] and line_list[1] and line_list[3] and \
                            line_list[27]:
                        company_rec_id = False
                        company_rec = self.env['res.company'].search([
                            ('name', '=', line_list[27])], limit=1)
                        if company_rec:
                            company_rec_id = company_rec.id

                        existing_rec = self.env['hr.ehours.sir.line'].search([
                            ('zone', '=', line_list[0]),
                            ('location', '=', line_list[1]),
                            ('identification', '=', line_list[3]),
                            ('company_id', '=', company_rec_id),
                            ('hr_ehours_sir_id', '=', rec.id)])
                    if not existing_rec:
                        rec_data = {}
                        if line_list[0]:
                            rec_data.update({'zone': line_list[0]})
                        if line_list[1]:
                            rec_data.update({'location': line_list[1]})
                        if line_list[2]:
                            rec_data.update({'position': line_list[2]})
                        if line_list[3]:
                            rec_data.update({'identification': line_list[3]})
                        if line_list[4]:
                            rec_data.update({'number': line_list[4]})
                        if line_list[5]:
                            rec_data.update({'name': line_list[5]})
                        if line_list[6]:
                            rec_data.update(
                                {'n_noct_charger_hours': line_list[6]})
                        if line_list[7]:
                            rec_data.update({'n_daylight_hours': line_list[7]})
                        if line_list[8]:
                            rec_data.update({'n_nightly_hours': line_list[8]})
                        if line_list[9]:
                            rec_data.update(
                                {'n_holiday_charge_hours': line_list[9]})
                        if line_list[10]:
                            rec_data.update(
                                {'n_extra_holiday_dayligth_hours':
                                     line_list[10]})
                        if line_list[11]:
                            rec_data.update(
                                {'n_extra_holiday_nigthlly_hours':
                                     line_list[11]})
                        if line_list[12]:
                            rec_data.update({'n_total_hours': line_list[12]})
                        if line_list[13]:
                            rec_data.update({'n_trans_sir_1': line_list[13]})
                        if line_list[14]:
                            rec_data.update({'n_trans_sir_2': line_list[14]})
                        if line_list[15]:
                            rec_data.update({'contador': line_list[15]})
                        if line_list[16]:
                            rec_data.update(
                                {'r_noct_charger_hours': line_list[16]})
                        if line_list[17]:
                            rec_data.update(
                                {'r_daylight_hours': line_list[17]})
                        if line_list[18]:
                            rec_data.update({'r_nightly_hours': line_list[18]})
                        if line_list[19]:
                            rec_data.update(
                                {'r_holiday_charge_hours': line_list[19]})
                        if line_list[20]:
                            rec_data.update(
                                {'r_extra_holiday_dayligth_hours':
                                     line_list[20]})
                        if line_list[21]:
                            rec_data.update(
                                {'r_extra_holiday_nigthlly_hours':
                                     line_list[21]})
                        if line_list[22]:
                            rec_data.update({'r_total_hours': line_list[22]})
                        if line_list[23]:
                            rec_data.update({'r_trans_sir_1': line_list[23]})
                        if line_list[24]:
                            rec_data.update({'r_trans_sir_2': line_list[24]})
                        if line_list[25]:
                            rec_data.update({'repeated': line_list[25]})
                        if line_list[26]:
                            rec_data.update({'extra_hours': line_list[26]})
                        if line_list[27]:
                            company_rec = self.env['res.company'].search([
                                ('name', '=', line_list[27])], limit=1)
                            if company_rec:
                                rec_data.update({'company_id': company_rec.id})
                            else:
                                rec_data.update({'company_id': False})
                        if line_list[28]:
                            rec_data.update({'database': line_list[28]})
                        if rec_data:
                            rec_data.update({'hr_ehours_sir_id': rec.id,
                                             'status': 'Success'})
                            self.env['hr.ehours.sir.line'].create(rec_data)


class HrEhoursSirLine(models.Model):
    """Hr Eehours Sir Line."""

    _name = "hr.ehours.sir.line"

    hr_ehours_sir_id = fields.Many2one('hr.ehours.sir')
    zone = fields.Char('ZONE')
    location = fields.Char('LOCATION')
    position = fields.Char('POSITION')
    identification = fields.Char('IDENTIFICATION')
    number = fields.Char('NUMBER')
    name = fields.Char('NAME')
    n_noct_charger_hours = fields.Float('RN')
    n_daylight_hours = fields.Float('D')
    n_nightly_hours = fields.Float('N')
    n_holiday_charge_hours = fields.Float('D/F')
    n_extra_holiday_dayligth_hours = fields.Float('EX FD')
    n_extra_holiday_nigthlly_hours = fields.Float('EX FN')
    n_total_hours = fields.Float('TOT_HORAS')
    n_trans_sir_1 = fields.Monetary('TRANSP SIR 1')
    n_trans_sir_2 = fields.Monetary('TRANSP SIR 2')
    contador = fields.Float('CONTADOR')
    r_noct_charger_hours = fields.Float('RN')
    r_daylight_hours = fields.Float('D')
    r_nightly_hours = fields.Float('N')
    r_holiday_charge_hours = fields.Float('D/F')
    r_extra_holiday_dayligth_hours = fields.Float('EX FD')
    r_extra_holiday_nigthlly_hours = fields.Float('EX FN')
    r_total_hours = fields.Float('TOT_HORAS')
    r_trans_sir_1 = fields.Float('TRANSP SIR 1')
    r_trans_sir_2 = fields.Float('TRANSP SIR 2')
    repeated = fields.Float('REPETIDOS')
    extra_hours = fields.Float('EXTRA HOURS')
    company_id = fields.Many2one(
        'res.company', string='COMPANY',
        default=lambda self: self.env.company)
    database = fields.Char('DATABASE')
    currency_id = fields.Many2one('res.currency', string='Currency')
    status = fields.Char(readonly=1)
