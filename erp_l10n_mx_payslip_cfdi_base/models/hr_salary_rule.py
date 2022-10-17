# coding: utf-8
from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    l10n_mx_code = fields.Char(
        'Our Code', help='Code defined by the company to this record, could '
        'not be related with the SAT catalog. Must be used to indicate the '
        'attribute "Clave" in the payslip lines, if this is empty will be '
        'used the value in the field "Code".')
    l10n_mx_sat_key_id = fields.Many2one('l10n.mx.sat.keys', 'SAT keys')
    l10n_mx_isr = fields.Boolean(string='ISR')
    l10n_mx_imss = fields.Boolean(string='IMSS')
    l10n_mx_automatic_isr = fields.Boolean(string='Automatic calculation')
    l10n_mx_visibility_automatic_isr =fields.Boolean(compute='_compute_l10n_mx_visibility_automatic_isr')


    def _compute_l10n_mx_visibility_automatic_isr(self):
        for record in self:
            if record.code == 'AUX_ISR' or record.code == 'AUX_OP002' or record.code == '002':
                record.l10n_mx_visibility_automatic_isr = True
            else:
                record.l10n_mx_visibility_automatic_isr = False


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    l10n_mx_payslip_type = fields.Selection([('O', 'O-Ordinary Payroll'), ('E', 'E-Extraordinary')], string='Type of payroll')
