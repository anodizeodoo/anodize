from odoo import fields, models, api, _
from odoo.exceptions import UserError


class HrScholarshipRegistration(models.Model):
    _name = 'hr.scholarship.registration'
    _description = 'Hr Scholarship Registration'
    _rec_name = 'payslip_run_id'

    amortization_date = fields.Date(
        string='Amortization Date',
        required=True,
    )

    payslip_run_id = fields.Many2one(
        'hr.payslip.run',
        string='Lotes',
        required=True
    )

    state = fields.Selection([
            ('draft', 'Draft'),
            ('validated', 'Validated'),
            ('loaded', 'Loaded')
        ],
        string='state',
        default='draft'
    )

    line_registration_ids = fields.One2many(
        'hr.scholarship.registration.line',
        'scholarship_registration_id',
        string='Line Registration',
        context={'active_test': False},
    )
    active_all = fields.Boolean('Marcar todos', default=False)
    unactive_all = fields.Boolean('Desmarcar todos', default=False)

    @api.onchange('active_all')
    def _onchange_line_active_registration_ids(self):
        if self.active_all:
            self.line_registration_ids.write({'active': True})
            self.write({'unactive_all': False})
    
    @api.onchange('unactive_all')
    def _onchange_line_unactive_registration_ids(self):
        if self.unactive_all:
            self.line_registration_ids.write({'active': False})
            self.write({'active_all': False})

    def action_confirm_validate(self):
        self.write({"state":"validated"})

    def back_to_draft(self):
        self.write({"state": "draft"})

    def action_confirm_registration(self):
        payslip_model = self.env['hr.payslip']
        payslip = []

        for line in self.mapped('line_registration_ids'):
            if not line.contract_id:
                raise UserError(_('The employee %s has not an active contract.') % (line.employee_id.name))
            if not line.scholarship_id:
                raise UserError(_('The employee %s does not have Family.') % (line.employee_id.name))
            vals={
                'name':line.name,
                'scholarship_registration_id': line.scholarship_id.id,
                'date': line.amortization_date,
                'contract_id': line.contract_id.id,
                'payslip_run_id': line.lote_id.id,
                'employee_id': line.employee_id.id,
                'company_id':self.env.company.id,
                'date_from':line.amortization_date,
                'date_to': line.amortization_date,
                'active_rule_sh': True,
            }
            payslip = payslip_model.sudo().create(vals)
        self.write({"state": "loaded"})

        return payslip


