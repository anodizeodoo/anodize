# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round


class TableNetAdjustments(models.Model):
    _name = "l10n.mx.table.net.adjustments"
    _description = 'Ajustes al Neto'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year, datetime.now().year - 5, -1)]

    year = fields.Selection(selection=_get_years, string='Año', default=lambda s: str(datetime.today().year), index=True)
    code = fields.Char(string='Código', index=True)
    name = fields.Char(string='Nombre', index=True)
    struct_ids = fields.Many2many('hr.payroll.structure', 'struct_net_adjustments_rel', string='Estructura Salarial')
    rounding = fields.Float(string='Precisión de redondeo', default=0.01, digits=(16, 2), index=True)
    strategy = fields.Selection([('amount_total', 'En el Importe Total')], string='Estrategia de Redondeo', default='amount_total', index=True)
    profit_account_id = fields.Many2one('account.account', string='Cuenta de Ganancias', company_dependent=True,
                                        domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]", index=True)
    loss_account_id = fields.Many2one('account.account', string='Cuenta de Pérdidas', company_dependent=True,
                                      domain="[('deprecated', '=', False), ('company_id', '=', current_company_id)]", index=True)

    @api.model_create_multi
    def create(self, vals_list):
        res_ids = super(TableNetAdjustments, self).create(vals_list)
        category_id = self.env['hr.salary.rule.category'].sudo().search([('id', '=', self.env.ref(
            'erp_l10n_mx_payslip_data.hr_salary_rule_category_deduction_mx').id)]).id or False
        for res in res_ids:
            for record in res.struct_ids:
                self.env['hr.salary.rule'].sudo().create({
                    'name': 'Ajustes al Neto',
                    'category_id': category_id,
                    'code': '099',
                    'struct_id': record.id,
                    'sequence': 2099,
                    'condition_select': 'none',
                    'amount_select': 'fix',
                    'quantity': 1,
                    'amount_fix': 0,
                    'is_net_adjustments': True,
                    'table_net_adjustments_id': res.id,
                })
        return res_ids

    def write(self, vals):
        res = super(TableNetAdjustments, self).write(vals)
        category_id = self.env['hr.salary.rule.category'].sudo().search([('id', '=', self.env.ref(
            'erp_l10n_mx_payslip_data.hr_salary_rule_category_deduction_mx').id)]).id or False
        for record in self.struct_ids:
            net_adjustments_id = self.env['hr.salary.rule'].sudo().search([
                ('is_net_adjustments', '=', True),
                ('table_net_adjustments_id', '=', self.sudo().id),
                ('struct_id', '=', record.sudo().id)
            ])
            if not net_adjustments_id:
                self.env['hr.salary.rule'].sudo().create({
                    'name': 'Ajustes al Neto',
                    'category_id': category_id,
                    'code': '099',
                    'struct_id': record.sudo().id,
                    'sequence': 2099,
                    'condition_select': 'none',
                    'amount_select': 'fix',
                    'quantity': 1,
                    'amount_fix': 0,
                    'is_net_adjustments': True,
                    'table_net_adjustments_id': self.sudo().id,
                })
        return res

    @api.constrains('rounding')
    def validate_rounding(self):
        for record in self:
            if record.rounding <= 0:
                raise ValidationError("Establezca un valor de Precisión de redondeo estrictamente positivo.")

    def round(self, amount):
        int_part, dec_part = int(str(amount).split(".")[0]), str(amount).split(".")[1]
        decimal_part = float(".".join(('0', dec_part)))
        if decimal_part != 0:
            if decimal_part == self.rounding:
                result = 0
            elif decimal_part < self.rounding:
                value = self.rounding - decimal_part
                result = value if value < decimal_part else -decimal_part
            else:
                value_max = 1 - decimal_part
                value_min = decimal_part - self.rounding
                result = value_max if value_max < value_min else -value_min
        else:
            result = 0
        return result
