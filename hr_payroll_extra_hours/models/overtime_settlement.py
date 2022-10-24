import datetime

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT
from odoo import fields, models


def get_months():
    months_choices = []
    for i in range(1, 13):
        months_choices.append(
            (str(i).rjust(2, '0'), datetime.date(
                2019, i, 1).strftime('%B')))
    return months_choices


class OvertimeSettlement(models.Model):
    """Overtime Settlement."""

    _name = "overtime.settlement"
    _rec_name = 'month'

    state = fields.Selection(
        [('draft', 'Draft'),
         ('process', 'Process')],
        string='Status', default='draft')

    month = fields.Selection(get_months(), string="Month")
    year = fields.Char()
    overtime_settlement_line_ids = fields.One2many(
        'overtime.settlement.line', 'overtime_settlement_id')

    def action_process(self):
        """Add One2many."""
        for rec in self:
            if rec.month and rec.year:
                name = rec.month + '-' + rec.year
                for pres_sub_rec in self.env['hr.ehours.pres.subs'].search([
                    ('name', '=', name),
                    ('state', '=', 'approved')]):
                    for line in pres_sub_rec.hr_ehours_pres_subs_line_ids:
                        employee_rec = self.env['hr.employee'].search([
                            ('identification_id', '=', line.identification)])
                        sup_hour = pre_hour = ''
                        if line.sup_start_date and line.sup_end_date:
                            sup_start = str(line.sup_start_date) + ' ' + \
                                        '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(line.sup_start_time * 60, 60)) + ':00'
                            sup_start = datetime.datetime.strptime(
                                sup_start, "%Y-%m-%d %H:%M:%S")
                            sup_end = str(line.sup_end_date) + \
                                      ' ' + '{0:02.0f}:{1:02.0f}'.format(
                                *divmod(line.sup_end_time * 60, 60)) + ':00'
                            sup_end = datetime.datetime.strptime(
                                sup_end, "%Y-%m-%d %H:%M:%S")
                            work_days = employee_rec._get_work_days_data_batch(
                                sup_start, sup_end)
                            if work_days.get(employee_rec.id, '') and \
                                    work_days.get(employee_rec.id, '').get(
                                        'hours', ''):
                                sup_hour = work_days.get(
                                    employee_rec.id, '').get('hours', '')
                        if line.pre_start_date and line.pre_end_date:
                            pre_start = str(line.pre_start_date) + ' ' + \
                                        '{0:02.0f}:{1:02.0f}'.format(
                                            *divmod(line.pre_start_time * 60, 60)) + ':00'
                            pre_start = datetime.datetime.strptime(
                                pre_start, "%Y-%m-%d %H:%M:%S")
                            pre_end = str(line.pre_end_date) + ' ' + \
                                      '{0:02.0f}:{1:02.0f}'.format(
                                          *divmod(line.pre_end_time * 60, 60)) + ':00'
                            pre_end = datetime.datetime.strptime(
                                pre_end, "%Y-%m-%d %H:%M:%S")
                            work_days = employee_rec._get_work_days_data_batch(
                                pre_start, pre_end)
                            if work_days.get(employee_rec.id, '') and \
                                    work_days.get(employee_rec.id, '').get(
                                        'hours', ''):
                                pre_hour = work_days.get(
                                    employee_rec.id, '').get('hours', '')
                        if sup_hour and pre_hour:
                            self.env['overtime.settlement.line'].create({
                                'overtime_settlement_id': rec.id,
                                'employee_id': employee_rec.id,
                                'pre_hour': pre_hour,
                                'sup_hour': sup_hour
                            })


class OvertimeSettlementLine(models.Model):
    """Overtime Settlement Line."""

    _name = "overtime.settlement.line"

    overtime_settlement_id = fields.Many2one('overtime.settlement')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    pre_hour = fields.Float()
    sup_hour = fields.Float()
