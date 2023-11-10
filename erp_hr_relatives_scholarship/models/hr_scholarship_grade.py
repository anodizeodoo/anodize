from datetime import datetime
from odoo import fields, models


class HrScholarshipGrade(models.Model):
    _name = 'hr.scholarship.grade'
    _description = 'Hr Scholarship Grade'
    _rec_name = 'grade'

    def years_selection(self):
        parameter_model = self.env['ir.config_parameter'].sudo()
        range_years_conf = parameter_model.get_param('range_years')
        years_conf = parameter_model.get_param('years')
        
        years = range(int(years_conf), int(years_conf) + int(range_years_conf))
        return [(str(year), str(year)) for year in years]

    year = fields.Selection(
        string='Year',
        required=True,
        selection=years_selection,
        default=lambda s: str(datetime.now().year)
    )

    date_capture = fields.Date(
        string='Date of Capture',
        required=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    grade = fields.Char(
        string='Grade',
        required=True
    )

    qualification = fields.Float(
        string='Qualification',
        required=True
    )

    amount = fields.Float(
        string='Amount',
        required=True
    )

    partner_id = fields.Many2one(
        'res.company',
        string='Partner',
        required=True,
        index=True,
    )

    active = fields.Boolean('Active', default=True, index=True)
