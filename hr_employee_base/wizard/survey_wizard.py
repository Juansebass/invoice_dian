# -*- coding: utf-8 -*-
from odoo import fields, models, _
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError


class SurveyInput(models.Model):
    _inherit = "survey.user_input"

    applicant_id = fields.Many2one('hr.applicant', string='Applicant')

class HrApplicant(models.Model):
    _inherit = "hr.applicant"
    
    response_ids = fields.One2many('survey.user_input', 'applicant_id', 'Respuestas')

class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    def _send_mail(self, answer):
        res = super()._send_mail(answer)
        if self.applicant_id:
            res.send()
        return res
    
    def action_invite(self):
        self.ensure_one()
        if self.applicant_id:
            survey = self.survey_id.with_context(clean_context(self.env.context))

            if not self.applicant_id.response_id:
                self.applicant_id.write({
                    'response_id': survey._create_answer(partner=self.applicant_id.partner_id).id
                })
            self.applicant_id.response_id.write({
                'applicant_id': self.applicant_id.id
            })
        return super().action_invite()


class SurveyWizard(models.TransientModel):
    _name = 'survey.wizard'
    _description = 'wizard Survey'

    def _default_applicant(self):
        return self.env['hr.applicant'].browse(self._context.get('active_id'))

    def _default_job(self):
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        return applicant.job_id
    
    def _default_survey(self):
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        return applicant.job_id.survey_ids

    applicant_id = fields.Many2one('hr.applicant', 'Aplicante', default=_default_applicant)
    job_id = fields.Many2one('hr.job','Puesto de Trabajo', default=_default_job)
    survey_ids = fields.Many2many('survey.survey', 'wizard_survey_rel','wizard_id','survey_id','Entrevistas', default=_default_survey)
    survey_id = fields.Many2one('survey.survey', 'Entrevista a Enviar') 
    response_id = fields.Many2one('survey.user_input', "Response", ondelete="set null")

    def action_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.response_id:
            response = self.survey_id._create_answer(partner=self.applicant_id.partner_id)
            response.applicant_id = self.applicant_id
            self.response_id = response.id
        else:
            response = self.response_id
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.access_token).action_start_survey()
    
    def action_send_survey(self):
        self.ensure_one()

        # # if an applicant does not already has associated partner_id create it
        # if not self.partner_id:
        #     if not self.partner_name:
        #         raise UserError(_('You must define a Contact Name for this applicant.'))
        #     self.partner_id = self.env['res.partner'].create({
        #         'is_company': False,
        #         'type': 'private',
        #         'name': self.partner_name,
        #         'email': self.email_from,
        #         'phone': self.partner_phone,
        #         'mobile': self.partner_mobile
        #     })
        dict_act_window = self.survey_id.with_context(default_applicant_id=self.applicant_id.id, default_partner_ids=self.applicant_id.partner_id.ids).action_send_survey()
        if not self.applicant_id.partner_id:
            dict_act_window["context"]["default_emails"] = self.applicant_id.email_from
        template = self.env.ref('hr_employee_base.mail_template_recruitment_interview', raise_if_not_found=False)
        dict_act_window["context"]["default_template_id"] = template.id or False
        return dict_act_window


class SurveyPrintWizard(models.TransientModel):
    _name = 'survey.print.wizard'
    _description = 'Print Survey'

    def _default_applicant_id(self):
        return self.env['hr.applicant'].browse(self._context.get('active_id'))
    
    def _default_input(self):
        applicant = self.env['hr.applicant'].browse(self._context.get('active_id'))
        return applicant.response_ids.ids

    applicant_id = fields.Many2one('hr.applicant', 'Aplicante', default=_default_applicant_id)
    response_ids = fields.Many2many('survey.user_input', 'wizard_input_rel','wizard_id','input_id','Respuestas', default=_default_input)
    response_id = fields.Many2one('survey.user_input', "Response")

    def action_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        # if not self.response_id:
        #     return self.response_id.survey_id.action_print_survey()
        # else:
        #     response = self.response_id
        #     return self.response_id.survey_id.with_context(survey_token=response.access_token).action_print_survey()
        return self.response_id.survey_id.action_print_survey(answer=self.response_id)


