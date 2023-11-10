import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    category_contract_id = fields.Many2one(
        related='contract_id.category_id',
        string='Category Contract',
    )


