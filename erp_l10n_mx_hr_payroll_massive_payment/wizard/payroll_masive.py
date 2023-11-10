from odoo import api, fields, models, _
from odoo.exceptions import UserError
from io import StringIO
import base64
import xlsxwriter
import pytz
from datetime import datetime

class MasivePayroll(models.Model):
    _name = 'massive.payroll.wizard'
    _description = 'allow generate archive txt with all payroll'

    name = fields.Char(string='Name')
    bank_selection = fields.Selection(
        string ='Select bank', 
        selection =[("banregio", "Banregio"), ("banbajio", "Banbajio"), ("bancomer", "Bancomer"), ("banorte", "Banorte"), ("santander", "Santander")],
         default = "banregio")

    file_generate = fields.Binary(string='File', readonly=True)
    file_name = fields.Char(string='File Name', readonly=True, invisible=True)
    file_generate_bool = fields.Boolean('', default=False, readonly=True, invisible=True)
    masive_payroll_payment_id = fields.Many2one(comodel_name='masive.payroll.payment', string='Massive Payroll Payment',invisible=True)
    hr_paylip_run_id = fields.Many2one(comodel_name='hr.payslip.run', string='Hr Payslip', related='masive_payroll_payment_id.hr_paylip_run_id')

    type_file = fields.Selection([("txt","txt"),("xls","xls")], string='File Output')
    

    def process(self):
        for record in self:
            bank_name = (dict(self._fields['bank_selection'].selection).get(self.bank_selection) or 'undefined')
            tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            #  
            now = datetime.now()
            _datetime = now.astimezone(tz)
            name_file = bank_name+"-" + now.strftime('%Y-%m-%d-%H-%M') + ".txt"
            data=StringIO()
            if record.bank_selection == "banregio":
                if record.type_file == "xls":
                    data = record.banregio_generate_xls()
                else:
                    raise UserError(_("Method not implemented"))
                #data = record.banregio_generate_txt()
            elif record.bank_selection == "banbajio":
                pass
                #data = record.banbajio_generate_txt()
            elif record.bank_selection == "bancomer":
                pass
                #data = record.bancomer_generate_txt()
            elif record.bank_selection == "banorte":
                pass
                #data = record.banorte_generate_txt()
            elif record.bank_selection == "santander":
                pass
                #data = record.santander_generate_txt()
            else:
                raise UserError(_("No bank selected"))
            print("retorna ultimo")
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'massive.payroll.wizard',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': record.id,
                'target': 'new',
            }

    def banregio_generate_xls(self):
        for record in self:
            result = []
            row = 0
            col = 0
            # Create a workbook and add a worksheet.
            tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
            now = datetime.now()
            _datetime = now.astimezone(tz)
            name_xls = 'Banregio'+"-" + now.strftime('%Y-%m-%d-%H-%M') +'.xlsx'
            workbook = xlsxwriter.Workbook(name_xls)
            ws = workbook.add_worksheet(name_xls)
            ws.write(row, col, 'Nómina')
            ws.write(row, col+1, 'Empleado')
            ws.write(row, col+2, 'Cuenta')
            ws.write(row, col+3, 'Monto')
            ws.set_column('A:A', 10)
            ws.set_column('B:B', 30)
            ws.set_column('C:C', 15)
            row += 1
            if record.masive_payroll_payment_id.payslip_ids:
                for line in record.masive_payroll_payment_id.payslip_ids:
                    ws.write(row, col, line.number)
                    ws.write(row, col+1, line.employee_id.name)
                    ws.write(row, col+2, line.employee_id.bank_account_id.acc_number)
                    ws.write(row, col+3, "%.2f" % line.net_wage)
                    row += 1

                workbook.close()
                file = open(name_xls, "rb")
                out = file.read()
                file.close()
                record.file_generate = base64.b64encode(out)
                record.file_name = name_xls
                record.file_generate_bool = True
                record.masive_payroll_payment_id.file_generate = base64.b64encode(out)
                record.masive_payroll_payment_id.file_name = name_xls
                print("genera")
            else:
                raise UserError(_("No payslip in this run"))

    def generate_txt(self, name_file, data):
        for record in self:
            try:
                    with open(name_file, mode='w') as f:
                        f.write(data)
                        f.close()

                    file = open(name_file, "rb")
                    out = file.read()
                    file.close()
                    record.file_generate = base64.b64encode(out)
                    record.file_name = name_file
                    record.file_generate_bool = True
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'massive.payroll',
                        'view_mode': 'form',
                        'view_type': 'form',
                        'res_id': record.id,
                        'target': 'new',
                    }
            except Exception as e:
                print('exception ' + str(e))