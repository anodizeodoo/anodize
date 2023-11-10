# -*- coding: utf-8 -*-

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    emergency_contact_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Emergency Contacts",
        relation="rel_employee_emergency_contact",
        domain=[("is_company", "=", False)],
    )
