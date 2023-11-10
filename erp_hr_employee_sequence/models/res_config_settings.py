from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    is_sequence = fields.Boolean(
        related="company_id.is_sequence",
        readonly=False
    )

    employee_id_sequence = fields.Many2one(
        related="company_id.employee_id_sequence",
        readonly=False,

    )
