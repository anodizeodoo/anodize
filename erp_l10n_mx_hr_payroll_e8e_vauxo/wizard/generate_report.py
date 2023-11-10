# -*- coding: utf-8 -*-
import base64
import xlsxwriter
from io import BytesIO
from datetime import datetime
from odoo import models, fields, api, _, tools
from odoo.exceptions import ValidationError


class GenerateReportWizard(models.TransientModel):
    _inherit = 'generate.report.wizard'

    def get_domain_for_not_signed(self):
        super().get_domain_for_not_signed()
        domain_not_sign = [('l10n_mx_cfdi_uuid', 'in', ['to_sign', False, ''])]
        return domain_not_sign