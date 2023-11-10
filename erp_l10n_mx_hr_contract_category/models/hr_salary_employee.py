from odoo import fields, models


class SalaryEmployee(models.Model):
    _inherit = 'l10n.mx.salary.employee'

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
        )

    contract_id_wage = fields.Monetary(
        related='contract_id.wage',
        currency_field='currency_id',
        string='Monthly Salary',
    )

    category_id = fields.Many2one(
        'hr.contract.category',
        string='Category',
    )

    wage_manual = fields.Float(
        string ='Monthly Salary New'
    )

    state = fields.Selection(
        string='Contrat State'
    )
