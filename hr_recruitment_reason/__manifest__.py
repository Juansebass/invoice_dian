# -*- coding: utf-8 -*-

# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Recruitment Reason',
    'version': '15.0.1.0.0',
    'author': 'Stefanini Sysman',
    'summary': 'Recruitment Reasons Customization for sysman',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'maintainer': 'Stefanini Sysman',
    'company': 'Stefanini Sysman S.A.S.',
    'website': "https://sysman.com.co",
    'depends': [
               'hr_recruitment',
    ],
    'data': [
        'views/recruitment_reason_views.xml',
        'views/hr_job_views.xml',
        #'views/job_position_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
