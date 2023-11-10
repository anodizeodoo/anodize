# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_mx_automatic_sequence_contracts = fields.Boolean(string='Contracts')
    number_days_contracts = fields.Integer(string='Number Days', default=1)

    contract_id_sequence = fields.Many2one(
        comodel_name="ir.sequence",
        string="Identificador de Secuencia",
        help="Patrón que se utilizará para la generación de identificadores de contratos",
        default=lambda self: self._default_contract_id_sequence(),
    )

    def _default_contract_id_sequence(self):
        sequence = getattr(self.env.user.sudo().company_id, 'contract_id_sequence', False)
        if not sequence:
            sequence = self.env.ref("erp_l10n_mx_hr_contract_holidays.seq_contract_number",
                                    raise_if_not_found=False)
        return sequence and sequence.id or False
