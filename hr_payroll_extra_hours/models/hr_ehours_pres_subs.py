import xlrd
import base64
import time
from datetime import date
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrEhoursPresSubs(models.Model):
    """Hr Ehours Pres Subs."""

    _name = "hr.ehours.pres.subs"
    _description = "Module to load and store Presences and Substitutions."

    @api.model
    def default_get(self, fields):
        """Month and Year will fill automatic."""
        rec = super(HrEhoursPresSubs, self).default_get(fields)
        rec.update({
            'name': time.strftime("%m-%Y")})
        return rec

    name = fields.Char("Month and Time", readonly="1")
    file = fields.Binary()
    hr_ehours_pres_subs_line_ids = fields.One2many(
        'hr.ehours.pres.subs.line', 'hr_ehours_pres_subs_id')
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
                last_sheet = workbook.sheet_by_index(0)
                # Will pick last sheet of the Excel Workbook
                for row in range(4, last_sheet.nrows):
                    row_list.append(last_sheet.row_values(row))
                if row_list:
                    for line_list in row_list:
                        domain = [
                            ('identification', '=', line_list[0]),
                            ('personal_number', '=', line_list[1]),
                            ('name', '=', line_list[2]),
                            ('cos_center', '=', line_list[3]),
                            ('position', '=', line_list[4]),
                            ('sup_start_time', '=', line_list[7]),
                            ('sup_end_time', '=', line_list[8]),
                            ('pre_start_time', '=', line_list[11]),
                            ('pre_end_time', '=', line_list[12]),
                            ('hr_ehours_pres_subs_id', '=', rec.id)]
                        if line_list[5]:
                            domain.append(
                                ('sup_start_date', '=', date(year=int(
                                    line_list[5][0:4]), month=int(
                                    line_list[5][4:6]), day=int(
                                    line_list[5][6:8]))))
                        if line_list[6]:
                            domain.append(('sup_end_date', '=', date(
                                year=int(line_list[6][0:4]), month=int(
                                    line_list[6][4:6]), day=int(
                                    line_list[6][6:8]))))
                        if line_list[9]:
                            domain.append(
                                ('pre_start_date', '=', date(year=int(
                                    line_list[9][0:4]), month=int(
                                    line_list[9][4:6]), day=int(
                                    line_list[9][6:8]))))
                        if line_list[10]:
                            domain.append(('pre_end_date', '=', date(
                                year=int(line_list[10][0:4]), month=int(
                                    line_list[10][4:6]), day=int(
                                    line_list[10][6:8]))))
                        duplicate_check_rec = self.env[
                            'hr.ehours.pres.subs.line'].search(domain)
                        if not duplicate_check_rec:
                            rec_data = {'status': 'Success'}
                            rec_data.update({
                                'identification': line_list[0],
                                'personal_number': line_list[1],
                                'name': line_list[2],
                                'cos_center': line_list[3],
                                'position': line_list[4],
                                'sup_start_time': line_list[7],
                                'sup_end_time': line_list[8],
                                'pre_start_time': line_list[11],
                                'pre_end_time': line_list[12],
                                'hr_ehours_pres_subs_id': rec.id})
                            if line_list[5]:
                                rec_data.update({
                                    'sup_start_date': date(year=int(
                                        line_list[5][0:4]), month=int(
                                        line_list[5][4:6]), day=int(
                                        line_list[5][6:8]))})
                            if line_list[6]:
                                rec_data.update({'sup_end_date': date(
                                    year=int(line_list[6][0:4]), month=int(
                                        line_list[6][4:6]), day=int(
                                        line_list[6][6:8]))})
                            if line_list[9]:
                                rec_data.update({'pre_start_date': date(
                                    year=int(
                                        line_list[9][0:4]), month=int(
                                        line_list[9][4:6]), day=int(
                                        line_list[9][6:8]))})
                            if line_list[10]:
                                rec_data.update({'pre_end_date': date(
                                    year=int(line_list[10][0:4]), month=int(
                                        line_list[10][4:6]), day=int(
                                        line_list[10][6:8]))})
                            self.env['hr.ehours.pres.subs.line'].create(
                                rec_data)


class HrEhoursPresSubsLine(models.Model):
    """Hr Ehours Pres Subs Line."""

    _name = "hr.ehours.pres.subs.line"

    hr_ehours_pres_subs_id = fields.Many2one('hr.ehours.pres.subs')
    identification = fields.Char()
    personal_number = fields.Char()
    name = fields.Char('FIRST NAME SURNAME')
    cos_center = fields.Char('MASTER COST CENTER')
    position = fields.Char()
    sup_start_date = fields.Date('START OF VALIDITY(SUBSTITUTION)')
    sup_end_date = fields.Date('END OF VALIDITY (SUBSTITUTION)')
    sup_start_time = fields.Float('START TIME (SUBSTITUTION)')
    sup_end_time = fields.Float('END TIME (SUBSTITUTION)')
    pre_start_date = fields.Date('START OF VALIDITY (ATTENDANCE)')
    pre_end_date = fields.Date('END OF VALIDITY(ATTENDANCE)')
    pre_start_time = fields.Float('START TIME (ATTENDANCE)')
    pre_end_time = fields.Float('END TIME (ATTENDANCE)')
    status = fields.Char(readonly=1)
    company_id = fields.Many2one(
        'res.company', string='COMPANY',
        default=lambda self: self.env.company)
