import xlrd
import base64
import time
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CargueHorasExtras(models.Model):
    """Cargue Horas Extras."""

    _name = "cargue.horas.extras"
    _description = "Cargue Horas Extras."
    _rec_name = 'create_uid'

    @api.model
    def default_get(self, fields):
        """Month and Year will fill automatic."""
        rec = super(CargueHorasExtras, self).default_get(fields)
        rec.update({
            'name': time.strftime("%m-%Y")})
        return rec

    name = fields.Char("Month and Time", readonly="1")
    file = fields.Binary()
    cargue_horas_extras_line_ids = fields.One2many(
        'cargue.horas.extras.line', 'cargue_horas_extras_id')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('approved', 'Process'),
         ('paid', 'Paid'),
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

    def action_paid(self):
        """Move to Paid."""
        for rec in self:
            rec.state = 'paid'

    def upload_data(self):
        """Upload data from Excel."""
        for rec in self:
            if self.search_count([
                ('state', 'in', ('draft', 'approved')),
                ('name', '=', rec.name)]) > 1:
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
                    identification = int(line_list[0])
                    start_date = datetime.strptime(
                        line_list[1], '%d.%m.%Y').date()
                    end_date = datetime.strptime(
                        line_list[2], '%d.%m.%Y').date()
                    concept = line_list[3]
                    quantity_hours = line_list[4]
                    existing_rec = self.env[
                        'cargue.horas.extras.line'].search([
                        ('identification', '=', identification),
                        ('start_date', '=', start_date),
                        ('end_date', '=', end_date),
                        ('concept', '=', concept),
                        ('quantity_hours', '=', quantity_hours),
                        ('cargue_horas_extras_id', '=', rec.id)])
                    if not existing_rec:
                        rec_data = {
                            'identification': identification,
                            'start_date': start_date,
                            'end_date': end_date,
                            'concept': concept,
                            'quantity_hours': quantity_hours,
                            'cargue_horas_extras_id': rec.id,
                            'status': 'Success'}
                        if rec_data:
                            self.env['cargue.horas.extras.line'].create(
                                rec_data)


class CargueHorasExtrasLine(models.Model):
    """Cargue Horas Extras Line."""

    _name = "cargue.horas.extras.line"

    cargue_horas_extras_id = fields.Many2one('cargue.horas.extras')
    identification = fields.Char('IDENTIFICATION')
    start_date = fields.Date()
    end_date = fields.Date()
    concept = fields.Char()
    quantity_hours = fields.Float()
    company_id = fields.Many2one(
        'res.company', string='COMPANY',
        default=lambda self: self.env.company)
    status = fields.Char(readonly=1)
