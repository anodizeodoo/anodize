# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_payroll_receipt_format = fields.Selection(
        [('sat_receipt', 'SAT Receipt'), ('other_receipt', 'Other Receipt')], string='Receipt',
        default='sat_receipt')
    l10n_mx_sent_email_bol = fields.Boolean(string='Sent Email', default=False)
    l10n_mx_sent_email = fields.Char(string='Email', default='')

    def get_default_category_perception_mx_taxed_id(self):
        category_perception_mx_taxed = self.sudo().env.ref('erp_l10n_mx_payslip_data.hr_salary_rule_category_perception_mx_taxed')
        return category_perception_mx_taxed.id if category_perception_mx_taxed else False

    def get_default_category_perception_mx_exempt_id(self):
        category_perception_mx_exempt = self.sudo().env.ref('erp_l10n_mx_payslip_data.hr_salary_rule_category_perception_mx_exempt')
        return category_perception_mx_exempt.id if category_perception_mx_exempt else False

    def get_default_category_deduction_mx_id(self):
        category_deduction_mx = self.sudo().env.ref('erp_l10n_mx_payslip_data.hr_salary_rule_category_deduction_mx')
        return category_deduction_mx.id if category_deduction_mx else False

    def get_default_category_other_mx_id(self):
        category_other_mx = self.sudo().env.ref('erp_l10n_mx_payslip_data.hr_salary_rule_category_other_mx')
        return category_other_mx.id if category_other_mx else False

    def get_default_category_aux_mx_id(self):
        category_aux_mx = self.sudo().env.ref('erp_l10n_mx_payslip_data.hr_salary_rule_category_aux_mx')
        return category_aux_mx.id if category_aux_mx else False

    def get_default_category_comp_mx_id(self):
        category_comp_mx = self.sudo().env.ref('hr_payroll.COMP')
        return category_comp_mx.id if category_comp_mx else False

    category_perception_mx_taxed_ids = fields.Many2many('hr.salary.rule.category', 'category_perception_mx_taxed_rel', string='Percepciones Gravadas')
    category_perception_mx_exempt_ids = fields.Many2many('hr.salary.rule.category', 'category_perception_mx_exempt_rel', string='Percepciones Exentas')
    category_deduction_mx_ids = fields.Many2many('hr.salary.rule.category', 'category_deduction_mx_rel', string='Deducciones')
    category_other_mx_ids = fields.Many2many('hr.salary.rule.category', 'category_other_mx_rel', string='Otros Pagos')
    category_aux_mx_ids = fields.Many2many('hr.salary.rule.category', 'category_aux_mx_rel', string='Auxiliares')
    category_comp_mx_ids = fields.Many2many('hr.salary.rule.category', 'category_comp_mx_rel', string='Contribuciones de la Empresa')

    category_perception_mx_taxed_id = fields.Many2one('hr.salary.rule.category', string='Percepción Gravada', default=get_default_category_perception_mx_taxed_id)
    category_perception_mx_exempt_id = fields.Many2one('hr.salary.rule.category', string='Percepción Exenta', default=get_default_category_perception_mx_exempt_id)
    category_deduction_mx_id = fields.Many2one('hr.salary.rule.category', string='Deducciones', default=get_default_category_deduction_mx_id)
    category_other_mx_id = fields.Many2one('hr.salary.rule.category', string='Otros Pagos', default=get_default_category_other_mx_id)
    category_aux_mx_id = fields.Many2one('hr.salary.rule.category', string='Auxiliar', default=get_default_category_aux_mx_id)
    category_comp_mx_id = fields.Many2one('hr.salary.rule.category', string='Contribución de la Empresa', default=get_default_category_comp_mx_id)

