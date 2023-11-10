# -*- coding: utf-8 -*-

from odoo import models, fields, api
from collections import defaultdict


class HrPayslipMassivePaymentView(models.Model):
    _name = 'masive.payroll.payment'
    _description = 'Hr Payslip Massive Payment View'

    name = fields.Char('Name')

    state = fields.Selection([('new', 'New'),
            ('validated', 'validated'),
            ('paid', 'paid'),
            ('conciliate', 'conciliate'),
        ], string='Status', default='new', readonly=True)
    
    date = fields.Date('date',default=fields.Date.today())
    hr_paylip_run_id = fields.Many2one('hr.payslip.run', string='Payslip Run',required=True)
    payslip_ids = fields.Many2many('hr.payslip', string='Payslips')
    date_start = fields.Date('Date From',related='hr_paylip_run_id.date_start',readonly=True)
    date_end = fields.Date('Date To', related='hr_paylip_run_id.date_end',readonly=True)
    l10n_mx_payment_date = fields.Date('Payment Date', related='hr_paylip_run_id.l10n_mx_payment_date',readonly=True)
    bank_id = fields.Many2one('res.bank', string='Bank',required=True)
    res_partner_bank_id = fields.Many2one('res.partner.bank', string='Bank Account',required=True)
    account_journal_id = fields.Many2one('account.journal', string='Journal',required=True)
    structure_id = fields.Many2one('hr.payroll.structure', string='Salary Structure',readonly=True)
    total_amount = fields.Float('Total Amount',compute='compute_payslip_ids' ,readonly=True)
    file_name = fields.Char('File Name',readonly=True)
    file_generate = fields.Binary('File',readonly=True)
    


    def set_validated(self):
        for record in self:
            record.state = 'validated'

    def set_paid(self):
        for record in self:
            record.state = 'paid'

    def set_conciliate(self):
        for record in self:
            record.state = 'conciliate'

    def load_payslips(self):
        if self.hr_paylip_run_id.slip_ids:
            hp_runs = self.sudo().mapped("hr_paylip_run_id.id")
            sql_query ="""select hp.id,hp.payslip_run_id from hr_payslip hp
                            where hp.payslip_run_id in %s and hp.state = 'done'"""
            self.env.cr.execute(sql_query, [tuple(hp_runs)])
            dict_pls = defaultdict(list)
            for pll in self.env.cr.fetchall():
                    dict_pls[pll[1]].append(pll[0])
            for record in self:
                all_run_vals = dict_pls.get(record.sudo().hr_paylip_run_id.id, {})
                if all_run_vals:
                    record.payslip_ids = [(6, 0, [x for x in all_run_vals])]
                    record.structure_id = record.payslip_ids[0].struct_id
                    record.compute_payslip_ids()
        else:
            self.payslip_ids = [(6, 0, [])]
        

    @api.depends('hr_paylip_run_id', 'payslip_ids')
    def compute_payslip_ids(self):
        if self.ids:
            hp_runs = self.sudo().mapped("hr_paylip_run_id").ids
            hp_pl = self.sudo().mapped("payslip_ids").ids
            if hp_runs and not hp_pl:
                sql_query="""select coalesce(sum(hpl.total),0),hp.payslip_run_id from hr_payslip hp
                    inner join hr_payslip_line hpl on 
                    hpl.slip_id =  hp.id 
                    where hp.payslip_run_id in %s group by hp.payslip_run_id"""
                self.env.cr.execute(sql_query, [tuple(hp_runs)])
                dict_pls = defaultdict(float)
                for pll in self.env.cr.fetchall():
                    dict_pls[pll[1]] = pll[0]

                for record in self:
                    record.total_amount = dict_pls.get(record.sudo().hr_paylip_run_id.id, 0.0)

            if hp_runs and hp_pl:
                sql_query="""select coalesce(sum(hpl.total),0), hp.payslip_run_id, hpl.slip_id from hr_payslip hp
                    inner join hr_payslip_line hpl on 
                    hpl.slip_id =  hp.id 
                    where hp.payslip_run_id in %s and hpl.slip_id in %s group by hp.payslip_run_id, hpl.slip_id"""
                self.env.cr.execute(sql_query, [tuple(hp_runs), tuple(hp_pl)])
                dict_pls = defaultdict(dict)
                for pll in self.env.cr.fetchall():
                    if dict_pls.get(pll[1], {}):
                        if not dict_pls[pll[1]].get(pll[2], False):
                            dict_pls[pll[1]][pll[2]] = 0.0
                    dict_pls[pll[1]][pll[2]] = pll[0]

                for record in self:
                    all_run_vals = dict_pls.get(record.sudo().hr_paylip_run_id.id, {})
                    total_rec = 0.0
                    if all_run_vals:
                        total_rec = sum(all_run_vals.get(x.id, 0.0) for x in
                                        record.sudo().payslip_ids if x.id in all_run_vals.keys())
                    record.total_amount = total_rec
        else:
            for record in self:
                record.total_amount = 0.0

        


    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('masive.payroll.payment')
        print(vals['name'])
        return super(HrPayslipMassivePaymentView, self).create(vals)

    @api.model
    @api.onchange('date')
    def context_default(self):
        result = self.env['hr.payslip.run'].search([('state', '=', 'close')])
        banks = self.env['res.partner.bank'].search([('bank_id', '=', self.sudo().bank_id.id)])

        ids_banks = []
        for x in banks:
            ids_banks.append(x.id)

        ids_result = []
        for x in result:
            ids_result.append(x.id)
        
        if self.hr_paylip_run_id:
            result = self.env['hr.payslip.run'].search([('state', '=', 'close'),
                                                        ('payslip_run_id', '=', self.sudo().hr_paylip_run_id.id)])
            ids_result = []
            for x in result:
                ids_result.append(x.id)
            return {'domain': {'hr_paylip_run_id': [('id', 'in', ids_result)]
                , 'res_partner_bank_id': [('id', 'in', ids_banks)]
                , 'payslip_ids': [('id', 'in', ids_result)]}
            }
        return {
            'domain': {'hr_paylip_run_id': [('id', 'in', ids_result)]
                , 'res_partner_bank_id': [('id', 'in', ids_banks)]}
        }


    @api.model
    @api.onchange('bank_id')
    def context_bank_id(self):
        banks = self.env['res.partner.bank'].search([('bank_id', '=', self.bank_id.id)])
        ids_banks = []
        for x in banks:
            ids_banks.append(x.id)
        journal = self.env['account.journal'].search([('bank_id', '=', self.bank_id.id)])
        ids_journal = []
        for x in journal:
            ids_journal.append(x.id)
        return {
            'domain': {'res_partner_bank_id': [('id', 'in', ids_banks)]
                , 'account_journal_id': [('id', 'in', ids_journal)]}
             }

    
    @api.model
    @api.onchange('hr_paylip_run_id')
    def context_hr_paylip_run_id(self):
        if self.hr_paylip_run_id:
            result = self.env['hr.payslip'].search(['&',('state', '=', 'done'),('payslip_run_id', '=', self.hr_paylip_run_id.id)])
            ids_result = []
            for x in result:
                ids_result.append(x.id)
            return {'domain': {
                 'payslip_ids': [('id', 'in', ids_result)]}
            }
