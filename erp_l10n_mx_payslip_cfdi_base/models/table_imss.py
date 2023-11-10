# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import fields, models, api, _


class TableImss(models.Model):
    _name = "l10n.mx.table.imss"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'IMSS'
    _rec_name = 'l10n_mx_imss_name'

    def _get_years(self):
        return [(str(x), str(x)) for x in range(datetime.now().year + 1, 2000, -1)]

    l10n_mx_imss_code = fields.Char(string='Code', tracking=True, index=True)
    l10n_mx_imss_name = fields.Char(string='Name', tracking=True, index=True)
    l10n_mx_imss_year = fields.Selection(string='Years', selection=_get_years, default=str(datetime.now().year), tracking=True, index=True)
    l10n_mx_imss_active = fields.Boolean(string='Status', default=True, tracking=True, index=True)
    l10n_mx_imss_line_ids = fields.One2many('l10n.mx.table.imss.line', 'l10n_mx_table_imss_id', string='Line IMSS', index=True)

    def write(self, vals):
        if vals.get('l10n_mx_imss_line_ids', False):
            change = []
            for line in vals['l10n_mx_imss_line_ids']:
                lines_id = self.l10n_mx_imss_line_ids.filtered(lambda f: f.id == line[1])
                if line[0] == 1:
                    if line[2].get('l10n_mx_imss_line_name', False):
                        change.append('{} <i class="fa fa-long-arrow-right align-middle ml-1"></i> Nombre: {} <i class="fa fa-long-arrow-right align-middle ml-1"></i> {}'.format(lines_id.l10n_mx_imss_line_name, lines_id.l10n_mx_imss_line_name, line[2]['l10n_mx_imss_line_name']))
                    if line[2].get('l10n_mx_imss_line_employee', False):
                        change.append('{} <i class="fa fa-long-arrow-right align-middle ml-1"></i> % Empleado: {} <i class="fa fa-long-arrow-right align-middle ml-1"></i> {}'.format(lines_id.l10n_mx_imss_line_name, lines_id.l10n_mx_imss_line_employee, line[2]['l10n_mx_imss_line_employee']))
                    if line[2].get('l10n_mx_imss_line_pattern', False):
                        change.append('{} <i class="fa fa-long-arrow-right align-middle ml-1"></i> % Patrón: {} <i class="fa fa-long-arrow-right align-middle ml-1"></i> {}'.format(lines_id.l10n_mx_imss_line_name, lines_id.l10n_mx_imss_line_pattern, line[2]['l10n_mx_imss_line_pattern']))
                if line[0] == 2:
                    self.message_post(body=_("El usuario %s a eliminado la Línea IMSS %s", self.env.user.login, lines_id.l10n_mx_imss_line_name))
                if line[0] == 0:
                    self.message_post(body=_("El usuario %s a adicionado la Línea IMSS %s", self.env.user.login, line[2]['l10n_mx_imss_line_name']))
            if change:
                lis = ''
                for c in change:
                    lis += '<li>{}</li>'.format(c)
                message = '<p>El usuario {} a editado las Líneas IMSS: </p> <ul> {} </ul>'.format(self.env.user.login, lis)
                self.message_post(body=_(message))
        return super(TableImss, self).write(vals)

    def _valid_field_parameter(self, field, name):
        # I can't even
        return name == 'tracking' or super()._valid_field_parameter(field, name)

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        if 'l10n_mx_imss_line_ids' not in default:
            l10n_mx_imss_line = []
            l10n_mx_imss_line_obj = self.env['l10n.mx.table.imss.line']
            for line in self.l10n_mx_imss_line_ids:
                line_imss_id = l10n_mx_imss_line_obj.create({
                    'l10n_mx_imss_line_name': line.l10n_mx_imss_line_name,
                    'l10n_mx_imss_line_employee': line.l10n_mx_imss_line_employee,
                    'l10n_mx_imss_line_pattern': line.l10n_mx_imss_line_pattern,
                })
                l10n_mx_imss_line.append(line_imss_id.id)
            default['l10n_mx_imss_line_ids'] = [(6, 0, l10n_mx_imss_line)]
        return super(TableImss, self).copy(default=default)


class TableImssLine(models.Model):
    _name = "l10n.mx.table.imss.line"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Line IMSS'

    l10n_mx_table_imss_id = fields.Many2one('l10n.mx.table.imss', string='Table IMSS', tracking=True, index=True)
    l10n_mx_imss_line_name = fields.Char(string='Name', tracking=True, index=True)
    l10n_mx_imss_line_employee = fields.Float(string='% Employee', digits=(12, 4), tracking=True, index=True)
    l10n_mx_imss_line_pattern = fields.Float(string='% Pattern', digits=(12, 4), tracking=True, index=True)

