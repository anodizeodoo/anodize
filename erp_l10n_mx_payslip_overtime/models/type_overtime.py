# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import logging

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError


class HrTypeOvertime(models.Model):
    _name = 'hr.type.overtime'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Type Overtime'

    name = fields.Char('Name')
    code = fields.Char('Code')


