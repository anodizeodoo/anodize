# -*- coding: utf-8 -*-
import re
import os
import base64
from odoo import models, fields, api
from collections import defaultdict
from datetime import datetime, date


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
    

    def refill_fields(self, text, size, right=True, fill=' ', upper=True):
        if not text:
            text = ''
        text = text.strip()
        if right:
            res = text.rjust(size, fill)
        else:
            res = text.ljust(size, fill)
        if upper:
            return res[:size].upper()
        else:
            return res[:size]

    def validate_char_fields(self, description):
        return re.sub("[^0-9a-zA-Z ]+", " ", description)

    def get_value_config(self, layout_config, value_config_str):
        if layout_config.default_char and not layout_config.use_default_char:
            value_config_str = layout_config.default_char
        elif layout_config.default_char and layout_config.use_default_char:
            value_config_str = '%s %s' % (layout_config.default_char, value_config_str)
        if layout_config.fill_column:
            value_config_str = value_config_str[:layout_config.column_length]
            value_config_str = self.refill_fields(value_config_str,
                                                   layout_config.column_length,
                                                   layout_config.fill_column_left,
                                                   layout_config.fill_using or ' ')
        return value_config_str.upper() if self.bank_id.use_upper_case else value_config_str

    def get_value_amount_str(self, amount_total_config, amount_total_str):
        if amount_total_config.default_char:
            amount_total_str = amount_total_config.default_char
        if amount_total_config.fill_column:
            if not amount_total_config.show_decimal:
                amount_total_str = ''.join(amount_total_str.split('.'))
            else:
                if len(amount_total_str) + 3 < amount_total_config.column_length:
                    if amount_total_str.count('.') == 0:
                        amount_total_str += '.00'
                    else:
                        if int(amount_total_str.split('.')[1]) == 0:
                            amount_total_str = amount_total_str.split('.')[0] + '.00'
                        elif len(amount_total_str.split('.')[1]) == 1:
                            amount_total_str = amount_total_str + '0'
            amount_total_str = self.refill_fields(amount_total_str,
                                                  amount_total_config.column_length,
                                                  amount_total_config.fill_column_left,
                                                  amount_total_config.fill_using)
        return amount_total_str

    def get_content_bancomer(self):
        to_write_in_file = []
        for payslip in self.payslip_ids:
            is_short_variant = True if self.bank_id.id == payslip.bank_id.id or (self.bank_id.code_bank_report == payslip.bank_id.code_bank_report) else False
            cod_layout_str = 'TNN' if is_short_variant else 'PSC'
            cargo_account_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_01'), payslip.bank_account_id.acc_number or '')
            clabe = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_02'), self.account_journal_id.bank_account_id.acc_number or '')
            currency_num_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_03'), '1')
            amount_total_str = self.get_value_amount_str(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_04'), str(round(payslip.net_wage, 2)))
            beneficiary_data = self.validate_char_fields(payslip.employee_id.name)
            beneficiary_data = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_05'), beneficiary_data)
            account_type = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_06'), '40')
            code_sat_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_07'), payslip.bank_id.l10n_mx_edi_code or '')
            description = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_08'), 'PAGO DE NOMINA')
            reference = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_09'), payslip.number)
            availability = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bancomer_10'), 'H')
            if is_short_variant:
                all_fields = [cod_layout_str, clabe, cargo_account_str, currency_num_str, amount_total_str, description]
            else:
                all_fields = [cod_layout_str, clabe, cargo_account_str, currency_num_str, amount_total_str,
                              beneficiary_data, account_type, code_sat_str, description, reference, availability]
            to_write_in_file.append(''.join(all_fields))
        return to_write_in_file

    def get_content_banorte(self):
        to_write_in_file = []
        for payslip in self.payslip_ids:
            clave_id_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_02'), '1')
            cargo_account_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_03'), self.account_journal_id.bank_account_id.acc_number or '')
            destination_account = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_04'), payslip.bank_account_id.acc_number or '')
            amount_total_str = self.get_value_amount_str(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_05'), str(round(payslip.net_wage, 2)))
            reference = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_06'), payslip.number)
            description = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_07'), 'PAGO DE NOMINA')
            currency_num_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_08'), '1')
            currency_dest_num_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_09'), '1')
            rfc_ord_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_10'), '')
            iva_str = '0.00'
            iva_config = self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_11')
            if iva_config.default_char:
                iva_str = iva_config.default_char
            if iva_config.fill_column:
                if not iva_config.show_decimal:
                    iva_str = ''.join(iva_str.split('.'))
                iva_str = self.refill_fields(iva_str,
                                             iva_config.column_length,
                                             iva_config.fill_column_left,
                                             iva_config.fill_using or ' ')
            e_mail_beneficiario_str = self.env.user.company_id.email if self.env.user.company_id.email else ''
            e_mail_beneficiario_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_12'), e_mail_beneficiario_str)
            date_application_str = datetime.combine(date.today(), datetime.min.time()).strftime("%d/%m/%Y")
            date_application_str = ''.join(date_application_str.split('/'))
            date_application_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_13'), date_application_str)
            payment_instruction = '%s %s' % (payslip.number, self.env.user.company_id.name)
            payment_instruction_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_banorte_14'), payment_instruction)
            all_fields = ['04', clave_id_str, cargo_account_str, destination_account, amount_total_str,
                          reference, description, currency_num_str, currency_dest_num_str, rfc_ord_str, iva_str,
                          e_mail_beneficiario_str, date_application_str, payment_instruction_str]
            to_write_in_file.append(''.join(all_fields))
        return to_write_in_file

    def get_content_santander(self):
        to_write_in_file = []
        for payslip in self.payslip_ids:
            cod_layout_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_01'), ' ')
            cargo_account_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_02'), self.account_journal_id.bank_account_id.acc_number or '')
            clabe_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_03'), payslip.bank_account_id.acc_number or '')
            receptor_bank_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_04'), ' ')
            beneficiary_data = self.validate_char_fields(payslip.employee_id.name)
            beneficiary_data = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_05'), beneficiary_data)
            code_sat_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_06'), self.bank_id.l10n_mx_edi_code)
            amount_total_config = self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_07')
            amount_total_str = str(round(payslip.net_wage, 2))
            if amount_total_config.default_char and not amount_total_config.use_default_char:
                amount_total_str = amount_total_config.default_char
            elif amount_total_config.default_char and amount_total_config.use_default_char:
                amount_total_str = '%s%s' % (amount_total_config.default_char, amount_total_str)
            if amount_total_config.fill_column:
                if not amount_total_config.show_decimal:
                    amount_total_str = ''.join(amount_total_str.split('.'))
                amount_total_str = self.refill_fields(amount_total_str,
                                                      amount_total_config.column_length,
                                                      amount_total_config.fill_column_left,
                                                      amount_total_config.fill_using or '')
            place_banxico_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_08'), '01001')
            description = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_09'), 'PAGO DE NOMINA')
            ref_orden_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_10'), payslip.number)
            e_mail_beneficiario_str = self.env.user.company_id.email if self.env.user.company_id.email else ''
            e_mail_beneficiario_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_11'), e_mail_beneficiario_str)
            way_application_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_12'), '')
            date_application_str = datetime.combine(date.today(), datetime.min.time()).strftime("%d/%m/%Y")
            date_application_str = ''.join(date_application_str.split('/'))
            date_application_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_santander_13'), date_application_str)
            all_fields = [cod_layout_str, cargo_account_str, clabe_str, receptor_bank_str, beneficiary_data,
                          code_sat_str, amount_total_str, place_banxico_str, description, ref_orden_str,
                          e_mail_beneficiario_str, way_application_str]
            to_write_in_file.append(''.join(all_fields))
        return to_write_in_file

    def get_content_bajio(self):
        to_write_in_file = []
        counter = 1
        for payslip in self.payslip_ids:
            is_short_variant = True if self.bank_id.id == payslip.bank_id.id or (self.bank_id.code_bank_report == payslip.bank_id.code_bank_report) else False
            payment_means_str = 'BCO' if is_short_variant else 'SPI'
            register_type_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_01'), '')
            sequence_number_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_02'), str(counter))
            counter += 1
            account_type_emissor_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_03'), '')
            account_number_emissor_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_04'), self.bank_id.bic or '')
            currency_code_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_05'), '')
            receptor_bank_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_06'), payslip.bank_id.l10n_mx_edi_code or '')
            amount_total_str = self.get_value_amount_str(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_07'), str(round(payslip.net_wage, 2)))
            date_application_str = datetime.combine(date.today(), datetime.min.time()).strftime("%d/%m/%Y")
            date_application_str = ''.join(date_application_str.split('/'))
            date_application_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_08'), date_application_str)
            account_type_receptor_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_10'), '01')
            account_number_receptor_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_11'), payslip.bank_account_id.acc_number or '')
            filler_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_12'), '')
            alias_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_13'), payslip.employee_id.l10n_mx_edi_rfc)
            iva_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_14'), '000000000000000')
            reference = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_15'), 'PAGO DE NOMINA')
            reference_spei_str = self.get_value_config(self.env.ref('erp_l10n_mx_hr_payroll_massive_payment.layout_configuration_bajio_16'), payslip.number)
            all_fields = [register_type_str, sequence_number_str, account_type_emissor_str, account_number_emissor_str,
                          currency_code_str, receptor_bank_str, amount_total_str, date_application_str,
                          payment_means_str, account_type_receptor_str, account_number_receptor_str, filler_str,
                          alias_str, iva_str, reference, reference_spei_str]
            to_write_in_file.append(''.join(all_fields))
        return to_write_in_file

    def generate_txt(self):
        url_temp = '/tmp/'
        name_file = self.name + "_" + self.bank_id.name + ".txt"
        if os.path.exists(url_temp):
            name = url_temp + name_file
        with open(name, 'w') as file:
            to_write_in_file = []
            if self.bank_id.code_bank_report == 'bancomer':
                to_write_in_file = self.get_content_bancomer()
            if self.bank_id.code_bank_report == 'banorte':
                to_write_in_file = self.get_content_banorte()
            if self.bank_id.code_bank_report == 'santander':
                to_write_in_file = self.get_content_santander()
            if self.bank_id.code_bank_report == 'bajio':
                to_write_in_file = self.get_content_bajio()
            lines_txt = []
            for value in to_write_in_file:
                if value == to_write_in_file[len(to_write_in_file) - 1]:
                    lines_txt.append(value)
                else:
                    lines_txt.append(value + '\n')
            file.writelines(lines_txt)
        content = open(name, 'rb').read()
        file_generate = base64.b64encode(content)
        self.write({
            'file_generate': file_generate,
            'file_name': name_file
        })

    def set_validated(self):
        for record in self:
            record.state = 'validated'
            record.generate_txt()

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
