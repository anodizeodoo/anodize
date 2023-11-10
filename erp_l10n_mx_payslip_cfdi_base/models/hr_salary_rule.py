# coding: utf-8
import calendar
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


def numOfDays(date1, date2):
    # check which date is greater to avoid days output in -ve number
    if date2 > date1:
        return (date2 - date1).days + 1
    else:
        return (date1 - date2).days

class HrRuleAuxIsr(models.Model):
    _name = 'hr.rule.aux.isr'
    _description = 'Auxiliar ISR Rules'

    rule_id = fields.Many2one('hr.salary.rule', string='Rule')
    aux_isr_rule_id = fields.Many2one('hr.salary.rule', string='Rule')


class HrRuleReportClassifier(models.Model):
    _name = 'hr.rule.report.classifier'
    _description = 'Report Classifier Rules'

    rule_id = fields.Many2one('hr.salary.rule', string='Rule')
    report_classifier_id = fields.Many2one('l10n.mx.report.classifier', string='Report classifier')
    sequence = fields.Integer(string='Sequence', index=True)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    l10n_mx_code = fields.Char(
        'Our Code', help='Code defined by the company to this record, could '
        'not be related with the SAT catalog. Must be used to indicate the '
        'attribute "Clave" in the payslip lines, if this is empty will be '
        'used the value in the field "Code".')
    l10n_mx_sat_key_id = fields.Many2one('l10n.mx.sat.keys', 'SAT keys')
    l10n_mx_isr = fields.Boolean(string='ISR')
    l10n_mx_imss = fields.Boolean(string='IMSS')
    l10n_mx_percep_grav_isr = fields.Boolean(string='PERCEP GRAV ISR')
    l10n_mx_automatic_isr = fields.Boolean(string='Automatic calculation')
    l10n_mx_visibility_automatic_isr = fields.Boolean(compute='_compute_l10n_mx_visibility_automatic_isr')
    rule_aux_isr_ids = fields.One2many('hr.rule.aux.isr', 'aux_isr_rule_id', 'Rule line')
    rule_report_classifier_ids = fields.One2many('hr.rule.report.classifier', 'rule_id', 'Report classifier line')
    # l10n_mx_net_adjustments = fields.Boolean(string='Ajuste al Neto')
    l10n_mx_sum_total = fields.Boolean(string='Es Salario Neto', default=False, index=True)
    is_net_adjustments = fields.Boolean(string='Es Ajuste al Neto', default=False, index=True)
    table_net_adjustments_id = fields.Many2one('l10n.mx.table.net.adjustments', 'Registro Ajuste al Neto', index=True)
    is_total_deduction = fields.Boolean(string='Es Total Deducciones', default=False, index=True)

    @api.onchange('l10n_mx_automatic_isr')
    def _onchange_l10n_mx_automatic_isr(self):
        if not self.l10n_mx_automatic_isr:
            self.amount_fix = 0
            self.quantity = 0

    def _compute_l10n_mx_visibility_automatic_isr(self):
        for record in self:
            if record.code == 'AUX_ISR' or record.code == 'AUX_OP002' or record.code == '002':
                record.l10n_mx_visibility_automatic_isr = True
            else:
                record.l10n_mx_visibility_automatic_isr = False


class HrPayrollStructure(models.Model):
    _inherit = 'hr.payroll.structure'

    l10n_mx_payslip_type = fields.Selection([('O', 'O-Ordinary Payroll'),
                                             ('E', 'E-Extraordinary')],
                                            string='Type of payroll')
    l10n_mx_stamp_payroll = fields.Boolean(string='Payroll stamp', default=False)


class HrPayrollStructureType(models.Model):
    _inherit = 'hr.payroll.structure.type'

    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    l10n_mx_table_isr_id = fields.Many2one('l10n.mx.table.isr', string='Table ISR')
    weekday = fields.Selection([('0', 'Monday'),
                                ('1', 'Tuesday'),
                                ('2', 'Wednesday'),
                                ('3', 'Thursday'),
                                ('4', 'Friday'),
                                ], string="Weekday", default='0')
    default_schedule_pay = fields.Selection(selection_add=[('daily', 'Daily'), ('decennial', 'Decennial')])
    periods_ids = fields.One2many('hr.payroll.structure.type.periods', 'type_id', string='Periods')
    l10n_mx_payroll_schedule_pay_id = fields.Many2one('l10n.mx.payroll.schedule.pay',
                                                      tracking=True,
                                                      index=True,
                                                      string='Periodo de Pago')
    code = fields.Char(string='Código', index=True)

    @api.constrains('code')
    def _validar_nombre_campo(self):
        for record in self:
            if record.code and not record.code.isalnum():
                raise ValidationError("El campo solo debe contener letras y números.")

    def generate_periods(self):
        if self.default_schedule_pay == 'daily':
            day = 1
        elif self.default_schedule_pay == 'weekly':
            day = 7
        elif self.default_schedule_pay == 'decennial':
            day = 12
        elif self.default_schedule_pay == 'bi-weekly':
            day = 15
        elif self.default_schedule_pay == 'monthly':
            day = 30
        elif self.default_schedule_pay == 'bi-monthly':
            day = 60
        elif self.default_schedule_pay == 'quarterly':
            day = 90
        elif self.default_schedule_pay == 'semi-annually':
            day = 180
        else:
            day = 365
        periods = []
        cont = 1
        if day == 7 or day == 12:
            if self.date_start.weekday() < int(self.weekday):
                days = int(self.weekday) - self.date_start.weekday()
                date_init = self.date_start + relativedelta(days=days)
            elif self.date_start.weekday() > int(self.weekday):
                days = self.date_start.weekday() - int(self.weekday)
                date = self.date_start - relativedelta(days=days)
                date_init = date + relativedelta(days=7)
            else:
                date_init = self.date_start
        else:
            date_init = self.date_start
        while (date_init + relativedelta(days=day)) <= self.date_end:
            if day == 15 and date_init.day == 16:
                date_end = date_init.replace(day=calendar.monthrange(date_end.year, date_end.month)[1])
            else:
                date_end = date_init + relativedelta(days=day - 1)

            num_days_c = numOfDays(date_init, date_end)
            periods.append(
                (0, 0, {
                    'order': cont,
                    'date_start': date_init,
                    'date_end': date_end,
                    'days': num_days_c,
                    'type_id': self.id,
                }))
            date_init = date_end + relativedelta(days=1)
            cont += 1
        self.write({'periods_ids': [(5, 0, 0)] + periods})


class HrPayrollStructureTypePeriods(models.Model):
    _name = 'hr.payroll.structure.type.periods'
    _description = 'Periods'

    type_id = fields.Many2one('hr.payroll.structure.type', string='Structure Type')
    order = fields.Integer(string='Order')
    date_start = fields.Date(string='Date start')
    date_end = fields.Date(string='Date end')
    days = fields.Integer(string='Days')

    @api.onchange('date_start', 'date_end')
    def dates_range_onchange(self):
        if self.date_start and self.date_end:
            date_init = self.date_start
            date_nd = self.date_end
            self.days = numOfDays(date_init, date_nd)


class HrSalaryRuleCategory(models.Model):
    _inherit = 'hr.salary.rule.category'

    report_classifier_id = fields.Many2one('l10n.mx.report.classifier', string='Report classifier')
