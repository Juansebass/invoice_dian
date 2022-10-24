
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class HrReportsConfig(models.Model):
    """Hr Reports Config."""
    _name = "hr.reports.config"

    name = fields.Char(related='model_id.name', store=True)
    model_id = fields.Many2one('ir.model', string='Model')

    type = fields.Selection([
        ('txt', 'TXT'),
        ('csv', 'CSV'),
        ('xls', 'XLS')], copy=False,
        default='txt')
    delimiter = fields.Char(size=1, copy=False)
    line_ids = fields.One2many(
        'hr.reports.config.line', 'hr_reports_config_id')


class HrReportsConfigLine(models.Model):
    """Hr Reports Config Line."""
    _name = "hr.reports.config.line"

    hr_reports_config_id = fields.Many2one('hr.reports.config')
    code = fields.Integer("Code")
    size = fields.Integer()
    data_type = fields.Selection([
        ('alphabetic', 'Alphabetic'),
        ('numeric', 'Numeric'),
        ('date', 'Date'),
        ('boolean', 'Boolean')],
        default='alphabetic')
    data_format = fields.Char()
    name = fields.Char()


class HrPilaReportConfig(models.Model):
    _name = 'hr.pila.report.config'
    _description = 'Config Model for HR Pila Report'

    code = fields.Char()
    name = fields.Char()
    line_ids = fields.One2many('hr.pila.report.config.line', 'pila_config_id', string='Events', required=False)


class HrPilaReportConfigLine(models.Model):
    _name = 'hr.pila.report.config.line'

    name = fields.Char(related='event_id.name')
    event_id = fields.Many2one('hr.pv.event', string='Events')
    pila_config_id = fields.Many2one('hr.pila.report.config')
