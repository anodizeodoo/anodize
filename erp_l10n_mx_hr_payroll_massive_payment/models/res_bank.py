# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging

from odoo import models, fields, api, _


class ResBank(models.Model):
    _inherit = 'res.bank'

    has_report = fields.Boolean(string="Layout Bancario")
    code_bank_report = fields.Selection([('bancomer', 'BANCOMER'),
                                         ('banorte', 'BANORTE'),
                                         ('santander', 'SANTANDER'),
                                         ('bajio', 'BAJIO')])
    layout_configuration_ids = fields.One2many('layout.configuration', 'bank_id', string="Configuracion de Layout")
    show_columns = fields.Boolean(string="Mostrar columnas")
    use_upper_case = fields.Boolean(string="Usar mayusculas")
    bank_alias_ids = fields.Many2many('bank.alias', 'res_bank_bank_alias_rel', 'res_bank_id', 'bank_alias_id', string="Claves de Transferencias")
    internal_code = fields.Char(string="Código interno")

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    alias_bank = fields.Char(string="Alias")
    is_bajio = fields.Boolean(string="Bajio", default=False)

    @api.onchange('bank_id')
    def _onchange_bajio(self):
        for rec in self:
            if rec.bank_id.l10n_mx_edi_code == '030':
                rec.is_bajio = True
            else:
                rec.is_bajio = False

class BankAlias(models.Model):
    _name = 'bank.alias'

    name = fields.Char(string="Alias")
    code_bank = fields.Char(string="Codigo")
    bank_id = fields.Many2one('res.bank', string="Banco")


class LayoutConfiguration(models.Model):
    _name = 'layout.configuration'
    _description = 'Layout Configuration'
    _order = 'sequence'

    column_name = fields.Char(string="Nombre de Columna")
    column_length = fields.Integer(string="Longitud")
    show_decimal = fields.Boolean(string="Usar Decimales", default=False)
    fill_column = fields.Boolean(string="Rellenar", default=True)
    fill_column_left = fields.Boolean(string="Rellenar hacia la izquierda", default=True)
    fill_using = fields.Char(string="Relleno con", default='0')
    bank_id = fields.Many2one('res.bank', string="Banco")
    sequence = fields.Integer(string='Secuencia', default=0)
    default_char = fields.Char(string="Cadena por defecto")
    use_default_char = fields.Boolean(string="Usar cadena al inicio del dato")
