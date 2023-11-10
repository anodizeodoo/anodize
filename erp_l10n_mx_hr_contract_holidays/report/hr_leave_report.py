# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.osv import expression


class LeaveReport(models.Model):
    _inherit = "hr.leave.report"



    @api.model
    def action_time_off_analysis(self):
        domain = [('holiday_type', '=', 'employee')]

        if self.env.context.get('active_ids') and not self.env.context.get('search_default_employee_id', False):
            domain = expression.AND([
                domain,
                [('employee_id', 'in', self.env.context.get('active_ids', []))]
            ])

        elif self.env.context.get('search_default_employee_id', False):
            domain = expression.AND([
                domain,
                [('employee_id', 'in', self.env.context.get('search_default_employee_id', []))]
            ])

        return {
            'name': _('Time Off Analysis'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave.report',
            'view_mode': 'tree,pivot,form',
            'search_view_id': [self.env.ref('hr_holidays.view_hr_holidays_filter_report').id],
            'domain': domain,
            'context': {
                'search_default_group_type': True,
                'search_default_year': True,
                'search_default_validated': True,
                'search_default_active_employee': True,
            }
        }