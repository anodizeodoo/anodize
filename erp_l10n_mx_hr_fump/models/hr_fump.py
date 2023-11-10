# -*- coding: utf-8 -*-

import babel
from datetime import datetime, time
from odoo import fields, models, tools, api, _
from odoo.exceptions import UserError, ValidationError

MOVEMENT_TYPE = [('contract', _('Contract')),
                   ('employee', _('Employee')),
                   ('holiday', _('Holiday'))]

class FumpMovementType(models.Model):
    _name = "hr.fump.movement.type"
    _description = "Fump Movement Type"

    name = fields.Char(string='Nombre', required="True", index=True)
    description = fields.Text(string='Descripción')
    type = fields.Selection([('prov', 'Provisional'), ('perm', 'Permanente')],
                            string='Tipo', index=True)
    movement_type = fields.Selection(MOVEMENT_TYPE, 'Tipo de movimiento', index=True)
    active = fields.Boolean(string='Active', default=True, index=True)
    reason = fields.Selection([('registration', 'Alta'),
                               ('discharge', 'BAJA'),
                               ('change', 'Cambio')],
                            string='Causa', index=True)

    
    def unlink(self):
        for motive in self.sudo():
            fump = self.env['hr.fump'].sudo().search([('movement_type_id', '=', motive.id)])
            if fump:
                raise ValidationError('No puedes eliminar este tipo de Movimiento de personal porque está siendo usado')
        return super(FumpMovementType, self).unlink()

class HrFump(models.Model):
    _name = "hr.fump"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Unique Format Of Personnel Movement"
    _order = "date_from asc"

    @api.model
    def _default_country(self):
        return self.env['res.country'].sudo().search([('code', '=', 'MX')], limit=1, order='create_date asc')

    name = fields.Char(string="Nombre", tracking=True, index=True)
    date_expedition = fields.Date("Fecha de expedición", copy=False,
                                  default=fields.Date.context_today, required=True,
                                  tracking=True, index=True)
    date_from = fields.Date(
        'Fecha inicio de vigencia',
        default=fields.Date.today,
        help="Period date of the Validity.",
        tracking=True, index=True
    )
    date_to = fields.Date(string='Fecha finalización',tracking=True, index=True)
    employee_id = fields.Many2one('hr.employee',string="Empleado",
                                  tracking=True, index=True)
    contract_id = fields.Many2one('hr.contract', string='Contracto actual',
                                  tracking=True, index=True)
    holiday_id = fields.Many2one("hr.leave", string='Petición de ausencia',
                                 tracking=True, index=True)
    rhs = fields.Selection([("1", '1'), ('2','2'),('3','3')],
                           string='Recursos Humanos para la Salud', index=True)
    movement_type_id = fields.Many2one('hr.fump.movement.type',string='Tipo de movimiento',
                                       tracking=True, index=True)
    movement_type_type = fields.Selection(MOVEMENT_TYPE, 'Tipo',
                                          related='movement_type_id.movement_type',
                                          store=True,
                                          tracking=True, index=True, compute_sudo=True)
    movement_type_name = fields.Char('Movement type name', related='movement_type_id.name',
                                          store=True,
                                     tracking=True, index=True, compute_sudo=True)

    department_id = fields.Many2one('hr.department',
                                    string="Departamento",
                                    tracking=True, index=True)

    country_id = fields.Many2one('res.country', string='País',
                                 tracking=True, 
                                 default=_default_country,
                                 index=True)
    state_id = fields.Many2one(
        'res.country.state', 'Estado',
        domain="[('country_id', '=', country_id)]",
        tracking=True, index=True)

    city_id = fields.Many2one('res.city',
                              string='Ciudad',
                              tracking=True, 
                              index=True)

    company_id = fields.Many2one('res.company', string='Compañía',
                                 required=True,
                                 index=True,
                                 default=lambda self: self.env.user.company_id,
                                 help="Company related")
    #Empleados
    employee_carnet = fields.Char(string="Carnet",tracking=True)
    certificate = fields.Char('Escolaridad',tracking=True)
    bank_account = fields.Char(string='N. DE CTA',tracking=True)
    ssnid = fields.Char('SSN No', help='SEG. SOCIAL',tracking=True)
    sinid = fields.Char('SIN No', help='CTA. SAR',tracking=True)
    employee_filiation = fields.Char(string="Filiación",tracking=True, index=True)
    employee_curp = fields.Char(string="CURP",tracking=True, index=True)
    employee_name = fields.Char('Nombre',tracking=True, index=True)
    address_home = fields.Char('Domicilio',tracking=True, index=True)
    company_employee = fields.Char(string='No. DE EMPLEADO',
                                   tracking=True, index=True)
    gender = fields.Char(string='Sexo',tracking=True, index=True)
    marital = fields.Char(string='EDO. CIVIL',
                          tracking=True, index=True)
    place_of_birth = fields.Char('Lugar de nacimiento',
                                 tracking=True, index=True)
    employee_country = fields.Char(string='Nacionalidad',
                                   tracking=True, index=True)

    #Contrato
    job = fields.Char(string="Puesto",tracking=True, index=True)
    wage = fields.Float('Salario',tracking=True, index=True)
    change_wage = fields.Boolean('Cambio de Salario',default=False,tracking=True, index=True)
    previous_salary = fields.Float('Salario previo',
                                   tracking=True, index=True)
    previous_job = fields.Char("Puesto de trabajo anterior",
                               tracking=True, index=True)
    department = fields.Char("Departamento vigente",
                             tracking=True, index=True)
    previous_department = fields.Char("Departamento anterior",
                                      tracking=True, index=True)

    loader_id = fields.Many2one('hr.fump.loader',
                                string="Importación", tracking=True, index=True)

    origin_type = fields.Selection([('manual', 'Manual'),
                                    ('import', 'Por importacion')],
                                    string='Tipo de Origen',
                                   index=True,
                                   default='manual')

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.contract_id = False
        if self.employee_id:
            if len(self.sudo().employee_id.contract_ids) == 1:
                possib_ctr = self.sudo().employee_id.contract_ids.filtered(lambda w: w.state == 'open')
                if possib_ctr:
                    self.contract_id = self.sudo().employee_id.contract_ids[0].id

    @api.model
    def get_year(self, date):
        return (date.year if date else '')

    @api.model
    def get_month(self, date):
        return (date.month if date else '')

    @api.model
    def get_day(self, date):
        return (date.day if date else '')

    @api.model
    def create(self, vals):
        employee = False
        if vals.get('employee_id',False):
            employee = self.env['hr.employee'].sudo().browse(vals.get('employee_id', False))
        elif vals.get('contract_id',False):
            contract = self.env['hr.contract'].sudo().browse(vals.get('contract_id',False))
            employee = contract.employee_id
        elif vals.get('holiday_id',False):
            holiday = self.env['hr.leave'].sudo().browse(vals.get('holiday_id', False))
            employee = holiday.employee_id
        if not employee:
            raise ValidationError("No existe un empleado relacioado para este movimiento de personal!!!")
        if employee:
            date_from = vals.get('date_from',False)
            ttyme = datetime.combine(fields.Date.from_string(date_from), time.min)
            locale = self.env.context.get('lang') or 'en_US'
            vals.update(name=_('FUMP of %s for %s') % (
                employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))))
        new_fumps = super(HrFump, self).create(vals)
        if new_fumps:
            for fump in new_fumps.filtered(lambda fmp: fmp.origin_type == 'manual'
                                                       and fmp.contract_id and fmp.employee_id):
                confirm_pending = True
                if not fump.contract_id.confirm_movement:
                    fump.contract_id.with_context(fump=True).write(dict(confirm_movement=True, last_fump_id=fump.id))
                    confirm_pending = False
                if not fump.contract_id.confirm_movement:
                    fump.employee_id.with_context(fump=True).write(dict(confirm_movement=True))
                    confirm_pending = False
                if confirm_pending:
                    raise ValidationError('Debe confirmar la modificación anterior antes de ejecutar una nueva!!!')
        return new_fumps