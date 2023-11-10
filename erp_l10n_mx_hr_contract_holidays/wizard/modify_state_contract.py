# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class ModifyStateContractWizard(models.TransientModel):
    _name = 'modify.state.contract.wizard'
    _description = 'Modify State Contract wizard'

    contract_id = fields.Many2one('hr.contract', string='Contract')

    @api.model
    def default_get(self, fields):
        res = super(ModifyStateContractWizard, self).default_get(fields)
        active_ids = self.env.context.get('active_ids')
        res['contract_id'] = active_ids[0]
        return res

    def update_state(self):
        self.contract_id.write({'state': 'close'})
        return True


