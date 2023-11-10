# -*- coding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    """Added academic, certification and experience details for employee."""

    _inherit = 'hr.employee'

    academic_ids = fields.One2many('hr.academic',
                                   'employee_id',
                                   'Academic Experiences',
                                   help="Academic Experiences")
    certification_ids = fields.One2many('hr.certification',
                                        'employee_id',
                                        'Certifications',
                                        help="Certifications")
    experience_ids = fields.One2many('hr.experience',
                                     'employee_id',
                                     ' Professional Experiences',
                                     help='Professional Experiences')
