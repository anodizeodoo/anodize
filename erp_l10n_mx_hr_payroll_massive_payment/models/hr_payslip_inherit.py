# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HRPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    bank_id = fields.Many2one('res.bank', string='Bank', related='employee_id.bank_id',readonly=True, compute_sudo=True)
    # res_partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',related='employee_id.res_partner_bank_id',readonly=True)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account', related='employee_id.bank_account_id', readonly=True, compute_sudo=True)
