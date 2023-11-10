# coding: utf-8

from datetime import timedelta
import calendar
from math import floor
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError

from odoo import api, fields, models, _

class L10nMxEdiJobRank(models.Model):
    _name = "l10n_mx_edi.job.risk"
    _description = "Used to define the percent of each job risk."

    name = fields.Char(help='Job risk provided by the SAT.', index=True)
    code = fields.Char(help='Code assigned by the SAT for this job risk.', index=True)
    percentage = fields.Float(help='Percentage for this risk, is used in the '
                              'payroll rules.', digits=(2, 6),)

class HrEmployeeType(models.Model):
    _name = "l10n.mx.hr.employee.type"
    _description = "Employee Type"

    name = fields.Char(string='Nombre', index=True)
    code = fields.Char(string='Código', index=True)
    active = fields.Boolean('Activo', default=True, index=True)

    def write(self, vals):
        res = super(HrEmployeeType, self).write(vals)
        if 'active' in vals:
            active = vals.get('active')
            if not active:
                employees = self.env['hr.employee'].search([('l10n_mx_edi_employee_type_id', '=', self.id)])
                if employees:
                    raise ValidationError(_('No se puede desactivar un tipo de empleado que está en uso.'))
        return res