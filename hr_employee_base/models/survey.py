# -*- coding: utf-8 -*-
from odoo.tools.safe_eval import safe_eval
from odoo import fields,models,api
from odoo.osv import expression


QUESTION_TYPE = {
    "text_box": "value_text_box",
    "char_box": "value_char_box",
    "numerical_box":"value_numerical_box",
    "date": "value_date",
    "datetime": "value_datetime",
    "simple_choice": "suggested_answer_id",
    "multiple_choice": "suggested_answer_id",
    "matrix": False
}

class SurveySurvey(models.Model):
    _inherit = 'survey.survey'
    
    manejo_interno = fields.Boolean(string="Manejo Interno")
    requisition_survey = fields.Boolean(string="Requisición")
    info_field_id = fields.Many2one("ir.model.fields",string="Campos requisición")

class SurveyQuestion(models.Model):
    _inherit = 'survey.question'

    req_field_id = fields.Many2one("ir.model.fields",string="Campos requisición")
    req_field_ttype = fields.Selection(related='req_field_id.ttype', string='field_name_type')
    req_field_m2o_model = fields.Char(related='req_field_id.relation', string='field_name_model')
    m2o_domain_field_ids = fields.Many2many('ir.model.fields', string='Campos relación')
    requisition_survey = fields.Boolean(string="Requisición", related='survey_id.requisition_survey')

    @api.onchange('req_field_id')
    def _onchange_req_field_id(self):
        if self.req_field_ttype=="many2one":
            model = self.sudo().env["ir.model"].search([("model", "=", self.req_field_m2o_model)])
            RelationModel = self.env[self.req_field_m2o_model]
            rec_field = model.field_id.filtered(lambda f: f.name==RelationModel._rec_name)
            self.m2o_domain_field_ids = [(4, rec_field.id, 0)]
        else:
            self.m2o_domain_field_ids = [(5,)]

    def get_relation_record(self, answer):
        Model = self.sudo().env[self.req_field_id.relation]
        domain = expression.OR([[(field.name, "=ilike", answer)] for field in self.m2o_domain_field_ids])
        return Model.search(domain, limit=1)


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'
    applicant_id = fields.Many2one('hr.applicant', 'Aplicante')

    def get_values_record_from_survey_input(self):
        vals = []
        for rec in self.filtered(lambda s: s.survey_id.requisition_survey):
            values = {}
            info_value=""
            answers = rec.user_input_line_ids.filtered(lambda a: a.question_id.req_field_id)
            for answer in answers:
                question = answer.question_id
                if question.req_field_id.ttype in ["char", "date", "datetime", "float", "integer", "monetary"]:
                    values[question.req_field_id.name] = answer[QUESTION_TYPE.get(question.question_type)]

                elif question.req_field_id.ttype == "boolean" and answer.suggested_answer_id.value:
                    if answer.suggested_answer_id.value.upper() in ["SI", "YES"]:
                        values[question.req_field_id.name] = True

                elif question.req_field_id.ttype == "text":
                    if question.req_field_id == rec.survey_id.info_field_id:
                        info_value = "{}\n*************************\n{}".format(answer.value_text_box, info_value)
                    else: 
                        values[question.req_field_id.name] = answer.value_text_box
                
                elif question.req_field_id.ttype == "selection":
                    selections = {value: key for key,value in safe_eval(question.req_field_id.selection)}
                    answer_value = answer.value_char_box or answer.suggested_answer_id.value
                    if answer_value in selections:
                        values[question.req_field_id.name] = selections.get(answer_value, False)
                    if  answer_value and answer_value not in selections:
                        info_value += "{}: {}\n".format(question.title, str(answer_value))
                
                elif question.req_field_id.ttype == "many2one":
                    answer_value = answer.value_char_box or answer.suggested_answer_id.value
                    record = question.get_relation_record(answer_value)
                    if record:
                        values[question.req_field_id.name] = record.id
                    if answer_value and not record:
                        info_value += "{}: {}\n".format(question.title, str(answer_value))
                else:
                    answer_value = answer.value_text_box or \
                        answer.value_char_box or \
                        answer.suggested_answer_id.value or \
                        answer.value_numerical_box or \
                        answer.value_date or answer.value_datetime
                    if answer_value:
                        info_value += "{}: {}\n".format(question.title, str(answer_value))
                        
                if rec.survey_id.info_field_id:
                    values[rec.survey_id.info_field_id.name] = info_value
            vals.append(values)
        return vals

    def write(self, vals):
        res = super(SurveyUserInput, self).write(vals)
        if vals.get('state', False)=="done":
            self.env["hr.requisition"].create(self.get_values_record_from_survey_input())
        return res