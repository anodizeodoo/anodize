# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

GENDER = {'male':'Masculino',
          'female':'Femenino',
          'other':''}

MARITAL = {'single':'SOLTERO',
        'married':'CASADO',
        'cohabitant':'OTRO.',
        'widower':'VIUDO',
        'divorced':'DIVORC'}

class FumpMovementTypeWzd(models.TransientModel):
    _name = 'hr.fump.movement.type.wzd'
    _description = "FUMP Wizard"

    @api.model
    def default_get(self, fields_list):
        defaults = super(FumpMovementTypeWzd, self).default_get(fields_list)
        active_model = self._context.get('default_res_model', False)
        active_id = self._context.get('default_res_id', False)
        if active_model and active_id:
            record = self.env[active_model].sudo().browse(active_id)
            if active_model == 'hr.contract' and record:
                defaults.update({
                    'contract_id':record.id,
                })
            if active_model == 'hr.employee' and record:
                defaults.update({
                    'employee_id':record.id,
                })
                if len(record.contract_ids) == 1:
                    contract = record.contract_ids[0]
                    defaults.update({
                        'contract_id': contract.id,
                    })
        return defaults

    @api.model
    def _default_country(self):
        return self.env['res.country'].sudo().search([('code', '=', 'MX')], limit=1, order='create_date')


    date_expedition = fields.Date("Fecha de expedición", copy=False,
                                  default=fields.Date.context_today,
                                  required=True, index=True)
    date_from = fields.Date(
        'Fecha inicio de vigencia',
        default=fields.Date.today, index=True,
        help="Period date of the Validity.",required=True,
    )
    date_to = fields.Date(string='Fecha finalización', index=True)
    employee_id = fields.Many2one('hr.employee', string="Empleado", index=True)
    contract_id = fields.Many2one('hr.contract', string='Contrato Actual', index=True)
    holiday_id = fields.Many2one("hr.leave", string='Petición de ausencia', index=True)
    rhs = fields.Selection([("1", '1'),
                            ('2', '2'),
                            ('3', '3')],
                           string='Recursos Humanos para la Salud', index=True)
    movement_type_id = fields.Many2one('hr.fump.movement.type',
                                       string='Tipo de movimiento',
                                       required=True, index=True)

    country_id = fields.Many2one('res.country', string='País',
                                 default=_default_country, index=True)
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        domain="[('country_id', '=', country_id)]", index=True)
    city_id = fields.Many2one('res.city', string='Ciudad', index=True)
    company_id = fields.Many2one('res.company', string='Compañía', required=True, index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Compañía")

    def _get_data_contract_fump(self):
        vals = {'date_from': self.sudo().date_from,
                'date_to': self.sudo().contract_id.date_end,
                'contract_id': self.sudo().contract_id.id,
                'employee_id': self.sudo().contract_id.employee_id.id,
                'movement_type_id': (self.sudo().movement_type_id.id or False),
                'company_id': (self.sudo().contract_id.company_id.id or False),
                'employee_carnet': self.sudo().contract_id.employee_id.carnet_id,
                'certificate': self.sudo().contract_id.employee_id.certificate,
                'bank_account': self.sudo().contract_id.employee_id.bank_account_id.acc_number,
                'ssnid': self.sudo().contract_id.employee_id.ssnid,
                'sinid': self.sudo().contract_id.employee_id.sinid,
                'employee_filiation': getattr(self.sudo().contract_id.employee_id, 'l10n_mx_rfc', '') ,
                'employee_curp': getattr(self.sudo().contract_id.employee_id, 'l10n_mx_curp', ''),
                'employee_name': self.sudo().contract_id.employee_id.name,
                'address_home': self.sudo().contract_id.employee_id.address_home_id.contact_address,
                # 'company_employee': self.sudo().contract_id.employee_id.company_employee_id,
                'gender': (GENDER[self.sudo().contract_id.employee_id.gender]
                           if self.contract_id.employee_id.gender else False),
                'marital': (MARITAL[self.sudo().contract_id.employee_id.marital]
                            if self.contract_id.employee_id.marital
                            and MARITAL.get(self.employee_id.marital, False) else False),
                'place_of_birth': self.sudo().contract_id.employee_id.place_of_birth,
                'employee_country': self.sudo().contract_id.employee_id.country_id.name,
                'job': self.sudo().contract_id.job_id.name,
                'wage': self.sudo().contract_id.wage,
        }
        if self.sudo().contract_id:
            vals.update(department=self.sudo().contract_id.department_id.name,department_id=self.contract_id.department_id.id)
            if self.sudo().contract_id.last_fump_id:
                vals.update(previous_salary=self.sudo().contract_id.last_fump_id.wage,
                            previous_job=self.sudo().contract_id.last_fump_id.job,
                            previous_department=self.sudo().contract_id.last_fump_id.department)
                if self.sudo().contract_id.wage != self.sudo().contract_id.last_fump_id.wage:
                    vals.update(change_wage=True)
                else:
                    vals.update(change_wage=False)
        return vals

    def _get_data_employee_fump(self):
        vals = {'date_from': self.sudo().date_from,
                'date_to': self.sudo().date_to,
                'employee_id': self.sudo().employee_id.id,
                'movement_type_id': (self.sudo().movement_type_id.id or False),
                'company_id': (self.sudo().company_id.id or False),
                'employee_carnet': self.sudo().employee_id.carnet_id,
                'certificate': self.sudo().employee_id.certificate,
                'bank_account': self.sudo().employee_id.bank_account_id.acc_number,
                'ssnid': self.sudo().employee_id.ssnid,
                'sinid': self.sudo().employee_id.sinid,
                'employee_filiation': self.sudo().employee_id.l10n_mx_rfc,
                'employee_curp': self.sudo().employee_id.l10n_mx_curp,
                'employee_name': self.sudo().employee_id.name,
                'address_home': self.sudo().employee_id.address_home_id.contact_address,
                # 'company_employee': self.sudo().employee_id.company_employee_id,
                'gender': (GENDER[self.sudo().employee_id.gender] if self.sudo().employee_id.gender else False),
                'marital': (MARITAL[self.sudo().employee_id.marital]
                            if self.sudo().employee_id.marital
                               and MARITAL.get(self.sudo().employee_id.marital,False) else False),
                'place_of_birth': self.sudo().employee_id.place_of_birth,
                'employee_country': self.sudo().employee_id.country_id.name,
                'job': self.sudo().employee_id.job_id.name,
                'wage': (self.sudo().contract_id.wage if self.sudo().contract_id else False)
                }
        if self.contract_id:
            vals.update(contract_id=self.sudo().contract_id.id,
                        department=self.sudo().contract_id.department_id.name,
                        department_id=self.sudo().contract_id.department_id.id)
            if self.sudo().contract_id.last_fump_id:
                vals.update(previous_salary=self.sudo().contract_id.last_fump_id.wage,
                            previous_job=self.sudo().contract_id.last_fump_id.job,
                            previous_department=self.sudo().contract_id.last_fump_id.department)
                if self.sudo().contract_id.wage != self.sudo().contract_id.last_fump_id.wage:
                    vals.update(change_wage=True)
                else:
                    vals.update(change_wage=False)
        else:
            vals.update(department=self.sudo().employee_id.department_id.name,
                        department_id=self.sudo().employee_id.department_id.id)
        return vals
    
    
    def btn_save(self):
        if self.sudo().contract_id:
            data_contract = self._get_data_contract_fump()
            self.env['hr.fump'].create(data_contract)
            self.contract_id.write({'confirm_movement':False})
        if self.sudo().employee_id:
            data_employee = self._get_data_employee_fump()
            self.env['hr.fump'].create(data_employee)
            self.employee_id.write({'confirm_movement':False})