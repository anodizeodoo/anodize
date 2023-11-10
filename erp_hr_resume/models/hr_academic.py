# -*- coding: utf-8 -*-

from odoo import models, fields


class HrAcademic(models.Model):
    """Added the details of the academic."""
    _name = 'hr.academic'
    _inherit = 'hr.curriculum'

    diploma = fields.Char('Diploma',
                          translate=True)
    study_field = fields.Char('Field of Study',
                              translate=True)
    activities = fields.Text('Activities and Associations',
                             translate=True)
