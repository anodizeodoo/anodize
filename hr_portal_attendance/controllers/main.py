# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.http import request
from datetime import datetime, timedelta
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class MyAttendance(http.Controller):
    
    @http.route(['/my/sign_in_attendance'], type='http', auth="user", website=True)
    def sign_in_attendace(self, **post):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("hr_portal_attendance.not_allowed_attendance")
        check_in = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if employee:
            vals = {
                    'employee_id': employee.id,
                    'check_in': check_in,
                    'check_in_web': True,
                    }
            attendance = request.env['hr.attendance'].sudo().create(vals)
            values = {
                    'attendance': attendance
                }
        return request.render('hr_portal_attendance.sign_in_attendance', values)

    @http.route(['/my/sign_out_attendance'], type='http', auth="user", website=True)
    def sign_out_attendace(self, **post):
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        if not employee:
            return request.render("hr_portal_attendance.not_allowed_attendance")
        
        no_check_out_attendances = request.env['hr.attendance'].search([
                    ('employee_id', '=', employee.id),
                    ('check_out', '=', False),
                ])
        check_out = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        attendance = no_check_out_attendances.write({'check_out': check_out})
        values = {
                    'attendance': attendance
                }
        return request.render('hr_portal_attendance.sign_out_attendance', values)


class CustomerPortal(CustomerPortal):
    
    @http.route()
    def account(self, **kw):
        response = super(CustomerPortal, self).account(**kw)
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        attendance_obj = request.env['hr.attendance']

        attendance_count = attendance_obj.sudo().search_count(
            [('employee_id', '=', employee.id),
             ])
        response.qcontext.update({
                'attendance_count': attendance_count,
        })
        return response

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'attendance_count' in counters:
            employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
            values['attendance_count'] = request.env['hr.attendance'].search_count([('employee_id', '=', employee.id)]) \
                if request.env['hr.attendance'].check_access_rights('read', raise_exception=False) else 0

        return values

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        attendance_obj = request.env['hr.attendance']

        attendance_count = attendance_obj.sudo().search_count(
            [('employee_id','=', employee.id)])
        values.update({'attendance_count': attendance_count})
        return values

    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, sortby=None, **kw):
        # response = super(CustomerPortal, self)
        values = self._prepare_portal_layout_values()
        employee = request.env['hr.employee'].search([('user_id', '=', request.env.user.id)])
        attendance_obj = http.request.env['hr.attendance']
        
        domain = [
            ('employee_id', '=', employee.id),
        ]
        # count for pager
        attendance_count = attendance_obj.sudo().search_count(domain)
        
        # pager
        # pager = request.website.pager(
        pager = portal_pager(
            url="/my/attendances",
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )
        
        no_check_out_attendances = request.env['hr.attendance'].sudo().search([
                     ('employee_id', '=', employee.id),
                     ('check_out', '=', False),
                 ])
        
        # content according to pager and archive selected
        attendances = attendance_obj.sudo().search(domain, limit=self._items_per_page, offset=pager['offset'])
        values.update({
            'attendances': attendances,
            'no_check_out_attendances': no_check_out_attendances,
            'page_name': 'attendance',
            'pager': pager,
            'default_url': '/my/attendances',
        })
        return request.render("hr_portal_attendance.display_attendances", values)
