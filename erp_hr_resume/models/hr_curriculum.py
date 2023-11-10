# -*- coding: utf-8 -*-

from odoo import models, fields


class HrCurriculum(models.Model):
    """Added the details of the curriculum."""

    _name = 'hr.curriculum'
    _description = "Employee's Curriculum"

    name = fields.Char('Name', required=True)
    employee_id = fields.Many2one('hr.employee',
                                  string='Employee',
                                  required=True)
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    description = fields.Text('Description')
    partner_id = fields.Many2one('res.partner',
                                 'Partner',
                                 help="Employer, School, University, "
                                      "Certification Authority")
    location = fields.Char('Location', help="Location")
    expire = fields.Boolean('Expire', help="Expire", default=True)
