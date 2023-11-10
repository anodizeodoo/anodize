from odoo import fields, models, api, _
from odoo.tools.misc import format_date
from odoo.exceptions import UserError


class HrScholarshipRegistrationLine(models.Model):
    _name = 'hr.scholarship.registration.line'
    _description = 'Hr Scholarship Registration Line'
    _order = 'active, employee_id'

    sequence = fields.Integer(
        'Sequence',
        compute='_compute_sequence',
        store=True
    )

    scholarship_registration_id = fields.Many2one(
        'hr.scholarship.registration',
        string='Scholarship Registration',
        index=True
    )

    lote_id = fields.Many2one(
        related='scholarship_registration_id.payslip_run_id',
        string='Lote',
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string='Employee',
        index=True,
    )

    number_employee = fields.Char(
        related='employee_id.number',
        string='No. Employee',
        readonly=True
    )

    contract_id = fields.Many2one(
        related='employee_id.contract_id',
        readonly=True
    )

    scholarship_id = fields.Many2one(
        'hr.employee.relative',
        string='Scholarship',
    )

    relationship_id = fields.Many2one(
        related='scholarship_id.relation_id',
        string='Relationship'
    )

    grade_id = fields.Many2one(
        'hr.scholarship.grade',
        string='Grade',
    )

    qualification = fields.Float(
        string='Qualification',
    )

    amount = fields.Float(
        string='Amount'
    )

    amount2 = fields.Float(
        string='Amount2'
    )

    amortization_date = fields.Date(
        related='scholarship_registration_id.amortization_date',
        string='Amortization Date',
    )

    observations = fields.Text(
        string='Observations'
    )

    state = fields.Selection(
        string='state',
        related='scholarship_registration_id.state'
    )

    struct_id = fields.Many2one(
        'hr.payroll.structure', string='Structure',
        compute='_compute_struct_id', store=True, readonly=False,
        help='Defines the rules that have to be applied to this payslip, according '
             'to the contract chosen. If the contract is empty, this field isn\'t '
             'mandatory anymore and all the valid rules of the structures '
             'of the employee\'s contracts will be applied.')

    name = fields.Char(
        string='Payslip Name', required=True,
        compute='_compute_name', store=True, readonly=False,)

    active = fields.Boolean('Active', default=True)

    @api.depends('scholarship_registration_id.line_registration_ids')
    def _compute_sequence(self):
        for line in self:
            _sequence = line.sequence = 0
            for l in line.scholarship_registration_id.line_registration_ids:
                _sequence += 1
                l.sequence = _sequence

    @api.onchange('active')
    def _onchange_active(self):
        if not self.active and self.scholarship_id:
            self.scholarship_id.write({'active': False})

    @api.depends('contract_id')
    def _compute_struct_id(self):
        for slip in self.filtered(lambda p: not p.struct_id):
            if not slip.contract_id and slip.employee_id:
                raise UserError(_('The employee %s has not an active contract.') % (slip.employee_id.name))
            slip.struct_id = slip.contract_id.structure_type_id.default_struct_id

    @api.depends('employee_id', 'struct_id', 'amortization_date')
    def _compute_name(self):
        for slip in self.filtered(lambda p: p.employee_id and p.amortization_date):
            lang = slip.employee_id.sudo().address_home_id.lang or self.env.user.lang
            context = {'lang': lang}
            payslip_name = slip.struct_id.payslip_name or _('Salary Slip')
            del context
            slip.name = '%(payslip_name)s - %(employee_name)s - %(dates)s' % {
                'payslip_name': payslip_name,
                'employee_name': slip.employee_id.name,
                'dates': format_date(self.env, slip.amortization_date, date_format="MMMM y", lang_code=lang)
            }
