# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    l10n_mx_payroll_receipt_format = fields.Selection(
        [('sat_receipt', 'SAT Receipt'),
         ('other_receipt', 'Other Receipt')],
        string='Receipt',
        related='company_id.l10n_mx_payroll_receipt_format',
        compute_sudo=True,
        readonly=False)

    category_perception_mx_taxed_ids = fields.Many2many(related='company_id.category_perception_mx_taxed_ids',
                                                        compute_sudo=True, readonly=False)
    category_perception_mx_exempt_ids = fields.Many2many(related='company_id.category_perception_mx_exempt_ids',
                                                         compute_sudo=True, readonly=False)
    category_deduction_mx_ids = fields.Many2many(related='company_id.category_deduction_mx_ids', compute_sudo=True,
                                                 readonly=False)
    category_other_mx_ids = fields.Many2many(related='company_id.category_other_mx_ids', compute_sudo=True,
                                             readonly=False)
    category_aux_mx_ids = fields.Many2many(related='company_id.category_aux_mx_ids', compute_sudo=True, readonly=False)
    category_comp_mx_ids = fields.Many2many(related='company_id.category_comp_mx_ids', compute_sudo=True,
                                            readonly=False)

    category_perception_mx_taxed_id = fields.Many2one(related='company_id.category_perception_mx_taxed_id',
                                                      compute_sudo=True, readonly=False)
    category_perception_mx_exempt_id = fields.Many2one(related='company_id.category_perception_mx_exempt_id',
                                                       compute_sudo=True, readonly=False)
    category_deduction_mx_id = fields.Many2one(related='company_id.category_deduction_mx_id', compute_sudo=True,
                                               readonly=False)
    category_other_mx_id = fields.Many2one(related='company_id.category_other_mx_id', compute_sudo=True, readonly=False)
    category_aux_mx_id = fields.Many2one(related='company_id.category_aux_mx_id', compute_sudo=True, readonly=False)
    category_comp_mx_id = fields.Many2one(related='company_id.category_comp_mx_id', compute_sudo=True, readonly=False)

