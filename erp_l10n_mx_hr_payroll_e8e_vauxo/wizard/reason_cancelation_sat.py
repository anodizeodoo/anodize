# -*- coding: utf-8 -*-
from odoo import models,fields,api, _

mx_cancel_reason = [('01', ('Comprobante emitido con errores con relación')),
                   ('02', ('Comprobante emitido con errores sin relación')),
                   ('03', ('No se llevó a cabo la operación')),
                   ('04', ('Operación nominativa relacionada en la factura global'))]

class CFDIReasonPayslipCancelation(models.TransientModel):
    _name ='cfdi.reason.payslip.cancelation'
    _description = 'CFDI Reason Cancelation'

    l10n_mx_cancel_reason = fields.Selection(
        selection=mx_cancel_reason,
        string=('Cancellation reason'), required=True)

    l10n_mx_foliosustitucion_cancel = fields.Char(string="Folio Substitution")

    def confirm(self):
        paysl = self.env['hr.payslip'].browse(self.env.context['active_ids'])
        ctx = {'l10n_mx_cancel_reason': self.l10n_mx_cancel_reason,
               'l10n_mx_foliosustitucion_cancel': self.l10n_mx_foliosustitucion_cancel or False}
        paysl.with_context(ctx).write(dict(l10n_mx_cancel_reason=self.l10n_mx_cancel_reason,
                                              l10n_mx_foliosustitucion_cancel=self.l10n_mx_foliosustitucion_cancel))
        if len(paysl) == 1:
            paysl.with_context(ctx).action_payslip_cancel()
        else:
            paysl.with_context(ctx).action_payslip_cancel()
