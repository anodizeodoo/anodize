from odoo import fields, models, api


class HistorySalaryEmployee(models.Model):
    _inherit = 'l10n.mx.history.salary.employee'

    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id,
        readonly=True
    )

    contract_id_wage = fields.Monetary(
        currency_field='currency_id',
        string='Monthly Salary',
    )

    category_id = fields.Many2one(
        'hr.contract.category',
        string='Category',
    )



