from odoo import fields, models, api


class ResConfig(models.TransientModel):
    _inherit = "res.config.settings"

    range_years = fields.Integer(
        string='Range Years',
        config_parameter='range_years',
        deafult=60
    )

    years = fields.Integer(
        string='Years',
        config_parameter='years',
        deafult=2022
    )
