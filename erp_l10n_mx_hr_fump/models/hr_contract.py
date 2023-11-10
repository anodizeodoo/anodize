# -*- coding: utf-8 -*-

import babel
from datetime import datetime, time
from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError, ValidationError

GENDER = {'male':'Masculino',
          'female':'Femenino',
          'other':''}

MARITAL = {'single':'SOLTERO',
        'married':'CASADO',
        'cohabitant':'OTRO.',
        'widower':'VIUDO',
        'divorced':'DIVORC'}

class HrContract(models.Model):
    _inherit = 'hr.contract'

    @api.depends('fump_ids')
    def _compute_fump(self):
        # fump_obj = self.env['hr.fump']
        # read_group_fump = fump_obj.read_group(
        #     [('contract_id', 'in', self.ids)],
        #     ['contract_id'], ['contract_id'])
        # attach_data = dict((res['contract_id'][0], res['contract_id_count']) for res in read_group_fump)
        for record in self:
            record.fump_count = len(record.sudo().fump_ids)
            # fump = fump_obj.search_read([('contract_id','=', record.id)], [],order='id desc', limit=1)
            # if record.sudo().fump_ids:
            #     record.last_fump_id = record.sudo().fump_ids[0].id

    confirm_movement = fields.Boolean(string="Confirmar Movimiento", default=False, index=True)
    fump_ids = fields.One2many('hr.fump','contract_id',string='Movimientos de personal')
    fump_count = fields.Integer(string="Movimiento de personal", compute='_compute_fump')
    last_fump_id = fields.Many2one('hr.fump',string='Ultimo FUMP')

    sync_up_loader_id = fields.Many2one('hr.fump.loader', string="Sincronizado", index=True)
    sync_up = fields.Boolean("Actualizado en la sincronización", default=False, index=True)
    sync_up_id = fields.Many2one('hr.fump.loader',"Última Sincronización por", default=False, index=True)
    
    def _get_data_fump(self,parent, movement_type):
        return {'date_from':parent.sudo().date_start,
            'date_to':parent.sudo().date_end,
            'contract_id':parent.sudo().id,
            'employee_id': parent.sudo().employee_id.id,
            'movement_type_id':(movement_type.sudo().id or False),
            'company_id':(parent.sudo().company_id.id or False),
            'employee_carnet': parent.sudo().employee_id.carnet_id,
            'certificate': parent.sudo().employee_id.certificate,
            'bank_account': parent.sudo().employee_id.bank_account_id.acc_number,
            'ssnid': parent.sudo().employee_id.ssnid,
            'sinid': parent.sudo().employee_id.sinid,
            'employee_filiation': getattr(parent.sudo().employee_id, "l10n_mx_rfc", ''),# revisar como tener este campo de forma comunitaria
            'employee_curp': getattr(parent.sudo().employee_id, "l10n_mx_curp", ''), # revisar como tener este campo de forma comunitaria
            'employee_name': parent.sudo().employee_id.name,
            'address_home': parent.sudo().employee_id.address_home_id.contact_address,
            'company_employee': parent.sudo().employee_id.identification_id,
            'gender': (GENDER[parent.sudo().employee_id.gender] if parent.sudo().employee_id.gender else False),
            'marital': (MARITAL[parent.sudo().employee_id.marital] if parent.sudo().employee_id.marital else False),
            'place_of_birth': parent.sudo().employee_id.place_of_birth,
            'employee_country': parent.sudo().employee_id.country_id.name,
            'job': parent.sudo().job_id.name,
            'wage': parent.sudo().wage,
            'department': parent.sudo().department_id.name,
            'department_id': parent.sudo().department_id.id,
            'previous_salary':parent.wage,
            'previous_job':parent.sudo().job_id.name,
            'previous_department':parent.sudo().department_id.name
        }

    @api.model
    def create(self, vals):
        parent = super(HrContract, self).create(vals)
        if not self._context.get('movement_type_id',False):
            movement_type_id = self.env.ref('erp_l10n_mx_hr_fump.hr_fump_movement_type_new_entry').id
        else:
            movement_type_id = self._context.get('movement_type_id')
        movement_type = self.env['hr.fump.movement.type']
        if movement_type_id:
            movement_type = self.env['hr.fump.movement.type'].browse(movement_type_id)
        data_fump = self._get_data_fump(parent, movement_type)
        self.env['hr.fump'].create(data_fump)
        return parent

    def reopen(self):
        movement_type_id = self.env.ref('erp_l10n_mx_hr_fump.hr_fump_movement_type_re_entry').id
        return super(HrContract, self.with_context(movement_type_id=movement_type_id)).reopen()

    def btn_change(self):
        self.ensure_one()
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
        action['domain'] = str([('contract_id', 'in', self.sudo().ids)])
        action['search_view_id'] = (
            self.env.ref('erp_l10n_mx_hr_fump.view_hr_fump_search').id,
        )
        return action

    # def write(self, vals):
        # for contract in self.sudo():
            # if contract.confirm_movement \
            #         and ('confirm_movement' not in vals
            #              or not ('confirm_movement' in vals
            #                      and not vals.get('confirm_movement'))) \
            #         and self._context.get('fump',True):
            #     raise ValidationError('Debe confirmar la modificación anterior antes de ejecutar una nueva')
            # if contract.state == 'open':
            #     if not (('state' in vals.keys() or 'confirm_movement' in vals.keys())
            #             and len(vals.keys()) == 1) and self._context.get('fump',True):
            #         vals['confirm_movement'] = True
        # return super(HrContract, self).write(vals)