# -*- coding: utf-8 -*-

from odoo import models, fields


class HrExperience(models.Model):
    """Added the details of the experience."""

    _name = 'hr.experience'
    _inherit = 'hr.curriculum'

    category = fields.Selection([('professional', 'Professional'),
                                 ('academic', 'Academic'),
                                 ('certification', 'Certification')],
                                'Category',
                                required=True,
                                default='professional',
                                help='Category')