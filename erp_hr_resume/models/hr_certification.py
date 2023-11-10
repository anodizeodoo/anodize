# -*- coding: utf-8 -*-

from odoo import models, fields


class HrCertification(models.Model):
    """Added the details of the certification."""

    _name = 'hr.certification'
    _inherit = 'hr.curriculum'

    certification = fields.Char('Certification Number',
                                help='Certification Number')
