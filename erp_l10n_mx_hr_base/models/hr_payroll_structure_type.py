from odoo import fields, models, api


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    contract_type_id = fields.Many2one('l10n.mx.payroll.contract.type', string='Contract type', required=1)
    type_of_benefit_id = fields.Many2one('l10n.mx.type.benefit', string='Type benefit', required=1)
