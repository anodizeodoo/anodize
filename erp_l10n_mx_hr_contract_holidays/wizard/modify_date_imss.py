# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ModifyDateImssWizard(models.TransientModel):
    _name = 'modify.date.imss.wizard'
    _description = 'Modify date IMSS wizard'

    contract_id = fields.Many2one('hr.contract', string='Contract')
    l10n_mx_date_imss = fields.Date(string='IMSS discharge date')

    @api.model
    def default_get(self, fields):
        res = super(ModifyDateImssWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        res['contract_id'] = active_ids[0]
        return res

    def update_date_imss(self):
        self.contract_id.write({'l10n_mx_date_imss': self.l10n_mx_date_imss})
        return True


