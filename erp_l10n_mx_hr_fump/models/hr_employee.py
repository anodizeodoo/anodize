# -*- coding: utf-8 -*-

import babel
from datetime import datetime, time
from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError, ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.depends('fump_ids')
    def _compute_fump(self):
        read_group_fump = self.env['hr.fump'].read_group(
            [('employee_id', 'in', self.ids)],
            ['employee_id'], ['employee_id'])
        attach_data = dict((res['employee_id'][0], res['employee_id_count']) for res in read_group_fump)
        for record in self:
            record.fump_count = attach_data.get(record.id, 0)

    confirm_movement = fields.Boolean(string="Confirmar Movimiento", default=False, index=True)
    fump_ids = fields.One2many('hr.fump', 'employee_id', string='Movimientos de personal')
    fump_count = fields.Integer(string="Movimiento de personal", compute='_compute_fump')

    # Datos empleados
    carnet_id = fields.Char('ID del carnet')

    sync_up_loader_id = fields.Many2one('hr.fump.loader',string="Sincronizado", index=True)
    sync_up = fields.Boolean("Actualizado en la sincronización",default=False, index=True)
    sync_up_id = fields.Many2one('hr.fump.loader',"Última Sincronización por", default=False, index=True)
    excel_row_index = fields.Integer('Número de la fila a partir de la cual se generó el empleado', index=True)

    def btn_change(self):
        action = {
            'name': _('FUMP Wizard'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'res_model': 'hr.fump.movement.type.wzd',
            'context': {
                'default_res_model': self._name,
                'default_res_id': self.sudo().id}
        }
        return action

    
    def action_view_fump(self):
        action = self.env.ref('erp_l10n_mx_hr_fump.action_hr_fump').read()[0]
        action['domain'] = str([('employee_id', 'in', self.sudo().ids)])
        action['search_view_id'] = (
            self.env.ref('erp_l10n_mx_hr_fump.view_hr_fump_search').id,
        )
        return action

    
    # def write(self, vals):
        # for employee in self.sudo().filtered(lambda emp: emp.contract_ids):
            # if employee.confirm_movement and ('confirm_movement'
            #                                   not in vals or
            #                                   not ('confirm_movement' in vals
            #                                        and not vals.get('confirm_movement'))) \
            #         and self._context.get('fump',True):
            #     raise ValidationError('Debe confirmar la modificación anterior antes de ejecutar una nueva')
            # if not ('confirm_movement' in vals.keys() and len(vals.keys()) == 1) and self._context.get('fump',True):
            #     vals['confirm_movement'] = True
        # return super(HrEmployee, self).write(vals)

    
    def action_update_employee_name(self):
        self.ensure_one()
        self._update_employee_name()
        return True

    def _update_employee_name(self):
        self.with_context(fump=False).name = self._get_name(self.lastname, self.firstname, self.lastname2)

class Department(models.Model):
    _inherit = "hr.department"

    def _update_employee_manager(self, manager_id):
        return super(Department, self.with_context(fump=False))._update_employee_manager(manager_id)

class ResourceResource(models.Model):
    _inherit = 'resource.resource'

    sync_up_loader_id = fields.Many2one('hr.fump.loader', string="Sincronizado", index=True)
    sync_up_id = fields.Many2one('hr.fump.loader',"Última Sincronización por", default=False, index=True)
    excel_row_index = fields.Integer('Número de la fila a partir de la cual se generó el emploeado', index=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sync_up_loader_id = fields.Many2one('hr.fump.loader', string="Sincronizado", index=True)
    sync_up_id = fields.Many2one('hr.fump.loader',"Última Sincronización por", default=False, index=True)
    excel_row_index = fields.Integer('Número de la fila a partir de la cual se generó el empleado', index=True)