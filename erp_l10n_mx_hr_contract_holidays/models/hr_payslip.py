# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, _


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    allocation_display = fields.Char(related='employee_id.allocation_display', compute_sudo=True)
    allocation_remaining_display = fields.Char(related='employee_id.allocation_remaining_display', compute_sudo=True)
    show_leaves = fields.Boolean(related='employee_id.show_leaves', compute_sudo=True)

    def action_time_off_dashboard(self):
        return {
            'name': _('Time Off Dashboard'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'views': [[self.env.ref('hr_holidays.hr_leave_employee_view_dashboard').id, 'calendar']],
            'domain': [('employee_id', 'in', self.employee_id.ids)],
            'context': {
                'employee_id': self.employee_id.id,
            },
        }
