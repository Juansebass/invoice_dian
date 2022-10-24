from odoo import api, fields, models, _, _lt
from datetime import date
from odoo.tools.misc import xlsxwriter
import io


class ZPreNominaReport(models.AbstractModel):
    _name = "zprenomina.report"
    _description = "zprenomina Report"
    _inherit = "account.report"

    filter_date = {'mode': 'range', 'filter': 'this_year'}
    filter_partner = True

    @api.model
    def _get_templates(self):
        templates = super(ZPreNominaReport, self)._get_templates()
        templates['line_template'] = 'account_reports.line_template_general_ledger_report'
        return templates

    @api.model
    def _get_columns_name(self, options):
        return [
            {'name': _('NIT')},
            {'name': _('Employee')},
            {'name': _('Fix Wage Amount')},
            {'name': _('Wage')},
            {'name': _('Payroll Name')},
            {'name': _('Payroll Date From')},
            {'name': _('Payroll Date To')},
            {'name': _('Contract Date Start')},
            {'name': _('Contract Type')},
            {'name': _('Company')},
            {'name': _('Job')},
            {'name': _('Concept Code')},
            {'name': _('Description')},
            {'name': _('Quantity')},
            {'name': _('Accruals')},
            {'name': _('Deductions')},
        ]

    @api.model
    def _get_report_name(self):
        return _("zprenomina-" + str(date.today().strftime("%d-%m-%y")))

    def _get_lines_zprenomina(self):
        lines = []

        wizard = self.get_parameters_wizard()

        sql = """SELECT emp.identification_id                                          emp_id,
                       emp.name                                                       emp_name,
                       con.fix_wage_amount                                            fix_wage_amount,
                       con.wage                                                       wage,
                       pay.name                                                       pay_name,
                       pay.date_from                                                  pay_date_from,
                       pay.date_to                                                    pay_date_to,
                       con.date_start                                                 contract_date_start,
                       c_type.name                                                    c_type_name,
                       com.name                                                       company_name,
                       coalesce(job.name, '')                                         job_name,
                       pay_line.code                                                  concept_code,
                       pay_line.name                                                  concept_name,
                       pay_line.days                                                  concept_days,
                       CASE WHEN pay_line.amount >= 0 THEN pay_line.amount ELSE 0 END concept_positive,
                       CASE WHEN pay_line.amount < 0 THEN pay_line.amount ELSE 0 END  concept_negative
                
                FROM hr_payslip pay
                         INNER JOIN res_company com ON (pay.company_id = com.id)
                         INNER JOIN hr_contract con ON (pay.contract_id = con.id)
                         LEFT JOIN hr_contract_type c_type ON (con.contract_type_id = c_type.id)
                         INNER JOIN hr_employee emp ON (pay.employee_id = emp.id)
                         LEFT JOIN hr_job job ON (emp.job_id = job.id)
                         INNER JOIN hr_payslip_line pay_line ON (pay.id = pay_line.slip_id)
                WHERE pay.company_id in %s
                AND pay.employee_id in %s 
                AND pay.date_from >= %s 
                AND pay.date_to <= %s 
                order by emp_name 
                        """

        companies = []
        for company in wizard['company_ids']:
            companies.append(company.id)

        employees = []
        for employee in wizard['employee_ids']:
            employees.append(employee.id)

        params = [tuple(companies), tuple(employees), str(wizard['date_from']), str(wizard['date_to'])]

        self.env.cr.execute(sql, params)
        columns = self.env.cr.dictfetchall()
        id = 0
        for column in columns:
            id += 1
            columns = [
                {'name': column['emp_name']},
                {'name': column['fix_wage_amount']},
                {'name': column['wage']},
                {'name': column['pay_name']},
                {'name': column['pay_date_from']},
                {'name': column['pay_date_to']},
                {'name': column['contract_date_start']},
                {'name': column['c_type_name']},
                {'name': column['company_name']},
                {'name': column['job_name']},
                {'name': column['concept_code']},
                {'name': column['concept_name']},
                {'name': column['concept_days']},
                {'name': self.format_value(float(column['concept_positive'])), 'class': 'number'},
                {'name': self.format_value(float(column['concept_negative'])), 'class': 'number'},

            ]
            line = {
                'id': id,
                'name': column['emp_id'][:128],
                'columns': columns,
                'level': 1,
            }
            lines.append(line)
        return lines

    def _get_lines(self, options, line_id=None):

        lines = self._get_lines_zprenomina()

        return lines

    def get_xlsx(self, options, response=None):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet(self._get_report_name()[:31])

        date_default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2, 'num_format': 'yyyy-mm-dd'})
        date_default_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'num_format': 'yyyy-mm-dd'})
        default_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        default_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})
        title_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'bottom': 2})
        super_col_style = workbook.add_format({'font_name': 'Arial', 'bold': True, 'align': 'center'})
        level_0_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 6, 'font_color': '#666666'})
        level_1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 13, 'bottom': 1, 'font_color': '#666666'})
        level_2_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_2_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_2_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666'})
        level_3_col1_style = workbook.add_format(
            {'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666', 'indent': 2})
        level_3_col1_total_style = workbook.add_format(
            {'font_name': 'Arial', 'bold': True, 'font_size': 12, 'font_color': '#666666', 'indent': 1})
        level_3_style = workbook.add_format({'font_name': 'Arial', 'font_size': 12, 'font_color': '#666666'})

        # Set the first column width to 50
        sheet.set_column(0, 16, 30)

        super_columns = self._get_super_columns(options)
        y_offset = bool(super_columns.get('columns')) and 1 or 0

        sheet.write(y_offset, 0, '', title_style)

        # Todo in master: Try to put this logic elsewhere
        x = super_columns.get('x_offset', 0)
        for super_col in super_columns.get('columns', []):
            cell_content = super_col.get('string', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
            x_merge = super_columns.get('merge')
            if x_merge and x_merge > 1:
                sheet.merge_range(0, x, 0, x + (x_merge - 1), cell_content, super_col_style)
                x += x_merge
            else:
                sheet.write(0, x, cell_content, super_col_style)
                x += 1
        for row in self.get_header(options):
            x = 0
            for column in row:
                colspan = column.get('colspan', 1)
                header_label = column.get('name', '').replace('<br/>', ' ').replace('&nbsp;', ' ')
                if colspan == 1:
                    sheet.write(y_offset, x, header_label, title_style)
                else:
                    sheet.merge_range(y_offset, x, y_offset, x + colspan - 1, header_label, title_style)
                x += colspan
            y_offset += 1
        ctx = self._set_context(options)
        ctx.update({'no_format': True, 'print_mode': True, 'prefetch_fields': False})
        # deactivating the prefetching saves ~35% on get_lines running time
        lines = self.with_context(ctx)._get_lines(options)

        if options.get('hierarchy'):
            lines = self._create_hierarchy(lines, options)
        if options.get('selected_column'):
            lines = self._sort_lines(lines, options)

        # write all data rows
        for y in range(0, len(lines)):
            level = lines[y].get('level')
            if lines[y].get('caret_options'):
                style = level_3_style
                col1_style = level_3_col1_style
            elif level == 0:
                y_offset += 1
                style = level_0_style
                col1_style = style
            elif level == 1:
                style = level_1_style
                col1_style = style
            elif level == 2:
                style = level_2_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_2_col1_total_style or level_2_col1_style
            elif level == 3:
                style = level_3_style
                col1_style = 'total' in lines[y].get('class', '').split(
                    ' ') and level_3_col1_total_style or level_3_col1_style
            else:
                style = default_style
                col1_style = default_col1_style

            # write the first column, with a specific style to manage the indentation
            cell_type, cell_value = self._get_cell_type_value(lines[y])
            if cell_type == 'date':
                sheet.write_datetime(y + y_offset, 0, cell_value, date_default_col1_style)
            else:
                sheet.write(y + y_offset, 0, cell_value, col1_style)

            # write all the remaining cells
            for x in range(1, len(lines[y]['columns']) + 1):
                cell_type, cell_value = self._get_cell_type_value(lines[y]['columns'][x - 1])
                if cell_type == 'date':
                    sheet.write_datetime(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value,
                                         date_default_style)
                else:
                    sheet.write(y + y_offset, x + lines[y].get('colspan', 1) - 1, cell_value, style)

        workbook.close()
        output.seek(0)
        generated_file = output.read()
        output.close()

        return generated_file

    def get_parameters_wizard(self):
        wizard = self.env['zconcept.report.wizard'].search([])[-1]
        return wizard
