# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class HrPayslipRun(models.Model):
    _inherit = "hr.payslip.run"

    def print_banking_dispersion_banregio(self):
        return self.env.ref('erp_l10n_mx_hr_reports.payroll_banking_dispersion_banregio').report_action(self, config=False)