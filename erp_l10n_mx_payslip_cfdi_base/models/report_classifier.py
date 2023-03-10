# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class ReportClassifier(models.Model):
    _name = "l10n.mx.report.classifier"
    _description = 'Report classifier'

    name = fields.Char(string='Name', translate=True)
    code = fields.Char(string='Code')

    def name_get(self):
        res = []
        for record in self:
            name = record.name
            if record.code:
                name = '{} {}'.format(record.code, name)
            res.append((record.id, name))
        return res
