# -*- coding: utf-8 -*-
# from odoo import http


# class /home/odoo1/escritorio/4-odoo/erpL10nMxHrPayrollMassivePayment(http.Controller):
#     @http.route('//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('/home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment.listing', {
#             'root': '//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment',
#             'objects': http.request.env['/home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment./home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment'].search([]),
#         })

#     @http.route('//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment//home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment/objects/<model("/home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment./home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('/home/odoo1/escritorio/4-odoo/erp_l10n_mx_hr_payroll_massive_payment.object', {
#             'object': obj
#         })
