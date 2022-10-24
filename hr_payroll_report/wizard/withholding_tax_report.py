from odoo import api, fields, models
from odoo.tools import date_utils
from odoo.tools.misc import xlsxwriter
from io import BytesIO
from datetime import date
import base64
import json


class WithholdingTax(models.TransientModel):
    _name = 'withholding.tax.wizard'

    report_type = fields.Selection([('pdf', 'PDF'), ('xlsx', 'XLSX')], string='Report Type', default=False)

    def print_xlsx(self):
        partners = []
        for payslip in self._context.get('active_ids'):
            obj_payslip = self.env['hr.payslip'].search([('id', '=', payslip)])
            for obj in obj_payslip:
                days_worked = obj.employee_id.get_days_annual(obj.date_to)

                data = {
                    'type_document': obj.employee_id.partner_id._l10n_co_edi_get_carvajal_code_for_identification_type(),
                    'identification_id': obj.employee_id.identification_id,
                    'first_surname': obj.employee_id.third_name,
                    'second_surname': obj.employee_id.fourth_name,
                    'first_name': obj.employee_id.first_name,
                    'second_name': obj.employee_id.second_name,
                    'name_found': obj.employee_id.found_layoffs_id.name,
                    'days_worked': days_worked,

                }

                partners.append(data)

        data = {
            'partners': partners,
        }

        return {
            'type': 'ir_actions_xlsx_download',
            'data': {'model': 'withholding.tax.wizard',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'RF ' + str(date.today().strftime("%d-%m-%y")),
                     }
        }

    def print_pdf(self):
        return self.env.ref('hr_payroll_report.action_report_withholding_tax').report_action(self)

    def get_xlsx_report(self, data, response):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        cell_format = workbook.add_format({'bold': True})
        sheet.set_column(0, 9, 30)  # Width of columns B:D set to 30.

        sheet.write('A1', 'Tipo de Documento', cell_format)
        sheet.write('B1', 'Numero Documento', cell_format)
        sheet.write_string('C1', 'Primer Apellido', cell_format)
        sheet.write_string('D1', 'Segundo Apellido', cell_format)
        sheet.write_string('E1', 'Primer Nombre', cell_format)
        sheet.write_string('F1', 'Segundo Nombre', cell_format)
        sheet.write('G1', 'Nombre Fondo', cell_format)
        sheet.write('H1', 'Dias trabajados', cell_format)

        # Start from the first cell. Rows and columns are zero indexed.
        row = 1
        col = 0

        # Iterate over the data and write it out row by row.
        for item in data['partners']:
            sheet.write(row, col, item['type_document'])
            sheet.write(row, col + 1, item['identification_id'])

            if item['first_surname']:
                sheet.write_string(row, col + 2, item['first_surname'])
            else:
                sheet.write_string(row, col + 2, "")

            if item['second_surname']:
                sheet.write_string(row, col + 3, item['second_surname'])
            else:
                sheet.write_string(row, col + 3, "")

            if item['first_name']:
                sheet.write_string(row, col + 4, item['first_name'])
            else:
                sheet.write_string(row, col + 4, "")

            if item['second_name']:
                sheet.write_string(row, col + 5, item['second_name'])
            else:
                sheet.write_string(row, col + 5, "")

            sheet.write(row, col + 6, item['name_found'])
            sheet.write(row, col + 7, item['days_worked'])
            row += 1

        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()
