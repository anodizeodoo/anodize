# -*- coding: utf-8 -*-

from odoo import fields, models, api

from datetime import datetime
from dateutil.relativedelta import relativedelta


class HrEmployeeRelative(models.Model):
    _name = 'hr.employee.relative'
    _description = 'HR Employee Relative'
    _order = 'active DESC'

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    relation_id = fields.Many2one(
        'hr.employee.relative.relation',
        string='Relation',
        required=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        domain=[
            '&', ('is_company', '=', False), ('type', '=', 'contact')
        ],
    )
    gender = fields.Selection(
        string='Gender',
        selection=[
            ('male', 'Male'),
            ('female', 'Female'),
            ('other', 'Other'),
        ],
    )
    date_of_birth = fields.Date(
        string='Date of Birth',
    )
    age = fields.Float(
        compute='_compute_age',
    )

    job = fields.Char()

    profession_id = fields.Many2one(
        string='Profesión',
        comodel_name='hr.employee.relative.professions',
    )

    phone_number = fields.Char()

    notes = fields.Text(
        string='Notes',
    )

    active = fields.Boolean('Active', default=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        for record in self:
            age = relativedelta(datetime.now(), record.date_of_birth)
            record.age = age.years + (age.months / 12)

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            self.name = self.partner_id.display_name
