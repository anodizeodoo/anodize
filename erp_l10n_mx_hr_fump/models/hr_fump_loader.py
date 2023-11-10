# -*- coding: utf-8 -*-
import io
import time
import xlrd
import json
import psycopg2, psycopg2.extensions
import datetime
import time
import babel
import sys, string, re

from audioop import error
from collections import defaultdict
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config, DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
from ..models import tools as loader_tools
from itertools import count

gender_dicc = {
    'MASCULINO': 'male',
    'FEMENINO': 'female'}

schedule_pay_dicc = {
    'DIARIO': '01',
    'SEMANALMENTE': '02',
    'BISEMANAL': '03',
    'QUINCENAL': '04',
    'MENSUAL': '05',
    'BIMENSUAL': '06',
    'UNIDADDETRABAJO': '07',
    'COMISION': '08',
    'PRECIOELEVADO': '09',
    'DECENAL': '10',
    'ANUAL': '11',
    'OTRO': '99'
}

marital_dicc = {
    'SOLTERO': 'single',
    'SOLTERA': 'single',
    'CASADO': 'married',
    'CASADA': 'married',
    'COHABITANTELEGAL': 'cohabitant',
    'UNIONLIBRE': 'cohabitant',
    'VIUDO': 'widower',
    'VIUDA': 'widower',
    'DIVORCIADO': 'divorced',
    'DIVORCIADA': 'divorced'
}

payment_method_dicc = {
    'TRANSFERENCIAELECTRONICADEFONDOS': 'electronic_funds_transfer',
    'EFECTIVO': 'cash',
    'CHEQUENOMINATIVO': 'nominal_check'
}

FUMP_FIELDS = [
    'name',
    'date_expedition',
    'date_from',
    'date_to',
    'employee_id',
    'contract_id',
    'movement_type_id',
    'department_id',
    'employee_carnet',
    'certificate',
    'ssnid',
    'sinid',
    'employee_filiation',
    'employee_curp',
    'employee_name',
    'gender',
    'marital',
    'place_of_birth',
    'job',
    'wage',
    'previous_salary',
    'previous_job',
    'department',
    'previous_department',
    'loader_id',
    'create_uid',
    'create_date',
    'company_id'
]

HR_CONTRACT_FIELDS = [
    'name',
    'employee_id',
    'department_id',
    'job_id',
    'date_start',
    'date_end',
    'wage',
    'state',
    'active',
    'create_uid',
    'create_date',
    'sync_up_loader_id',
    'resource_calendar_id',
    'company_id',
    'sync_up_id'
]

HR_EMPLOYEE_FIELDS = [
    'name',
    'lastname2',
    'lastname',
    'firstname',
    'l10n_mx_rfc',
    'l10n_mx_curp',
    'gender',
    'marital',
    'birthday',
    'place_of_birth',
    'ssnid',
    'study_field',
    'job_id',
    'department_id',
    'address_home_id',
    'address_id',
    'resource_id',
    'active',
    'company_id',
    'certificate',
    'resource_calendar_id',
    'bank_account_id',
    'country_id',
    'carnet_id',
    'create_uid',
    'create_date',
    'sync_up_loader_id',
    'excel_row_index',
    'sync_up_id',
]

RESOURCE_RESOURCE_FIELDS = [
    'name',
    'resource_type',
    'time_efficiency',
    'calendar_id',
    'tz',
    'active',
    'company_id',
    'create_uid',
    'create_date',
    'sync_up_loader_id',
    'excel_row_index',
    'sync_up_id',
]

RES_PARTNER_FIELDS = [
    'name',
    'country_id',
    'street',
    'street2',
    'zip',
    'state_id',
    'email',
    'active',
    'company_id',
    'type',
    'employee',
    'tz',
    'lang',
    'display_name',
    'create_uid',
    'create_date',
    'excel_row_index',
    'sync_up_id'
]

BIG_DATA_FIELDS = [
    'loader_id',
    'no_employee',
    'employee_status',
    'employee_full_name',
    'employee_firstname',
    'employee_lastname',
    'employee_lastname2',
    'contract_date_start',
    'contract_date_end_1',
    'contract_reentry_date_1',
    'contract_date_end_2',
    'contract_reentry_date_2',
    'contract_date_end_3',
    'department',
    'job',
    'id_job_in_contract',
    'nivel',
    'tabulator',
    'salary',
    'pantry',
    'passage',
    'monthly_gross_salary',
    'period_type',
    'payment_method',
    'banck_account',
    'account',
    'employee_gender',
    'employee_rfc',
    'employee_curp',
    'employee_country',
    'employee_ssnid',
    'employee_birthdate',
    'employee_age',
    'employee_phone',
    'employee_mun_of_birth',
    'employee_est_of_birth',
    'employee_email',
    'employee_street',
    'employee_ext_no',
    'employee_int_no',
    'employee_colony',
    'employee_municipality',
    'employee_state',
    'employee_cp',
    'employee_marital',
    'employee_certificate',
    'employee_study_field',
    'employee_carnet',
    'withdrawal_reason',
    'employee_bloodtype_factor',
    'sheet_name'
]

BIG_DATA_FIELDS_TEMP = [
    'loader_id',
    'no_employee',
    'employee_status',
    'employee_full_name',
    'employee_firstname',
    'employee_lastname',
    'employee_lastname2',
    'contract_date_start',
    'contract_date_end_1',
    'contract_reentry_date_1',
    'contract_date_end_2',
    'contract_reentry_date_2',
    'contract_date_end_3',
    'department',
    'job',
    'id_job_in_contract',
    'nivel',
    'tabulator',
    'salary',
    'pantry',
    'passage',
    'monthly_gross_salary',
    'period_type',
    'payment_method',
    'banck_account',
    'account',
    'employee_gender',
    'employee_rfc',
    'employee_curp',
    'employee_country',
    'employee_ssnid',
    'employee_birthdate',
    'employee_age',
    'employee_phone',
    #'employee_mun_of_birth',
    #'employee_est_of_birth',
    #'employee_email',
    #'employee_street',
    #'employee_ext_no',
    #'employee_int_no',
    #'employee_colony',
    #'employee_municipality',
    #'employee_state',
    #'employee_cp',
    #'employee_marital',
    #'employee_certificate',
    #'employee_study_field',
    #'employee_carnet',
    #'withdrawal_reason',
    #'employee_bloodtype_factor',
    #'sheet_name'
]


class HrFumpLoader(models.Model):
    _name = 'hr.fump.loader'
    _description = 'Importación de FUMP'

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    @api.model
    def default_get(self, fields_list):
        res = super(HrFumpLoader, self).default_get(fields_list)
        res['name'] = self.env['ir.sequence'].next_by_code('hr.fump.loader.sequence')
        return res

    name = fields.Char(string='Nombre', copy=False, readonly=True,
                       index = True,
                       states={'draft': [('readonly', False)]})
    file = fields.Binary(string='Archivo de Sincronización',
                         copy=False,
                         attachment=True, required=True)
    file_name = fields.Char(string='Nombre de Archivo de Sincronización',
                            index=True,
                            copy=False)
    fump_file = fields.Binary(string='Archivo de Movimiento de Personal',
                              copy=False,
                              attachment=True)
    fump_file_name = fields.Char(string='Nombre de Archivo de Movimiento de Personal', index=True, copy=False)
    user_id = fields.Many2one(
        'res.users',
        string='User',
        help='Usuario que realiza la importación',
        default=_default_user,
        index=True,
        copy=False
    )
    date = fields.Datetime(string="Fecha", default=fields.Datetime.now,
                           index=True,
                           copy=False)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('xlsx_loaded', 'Archivo de Sincronización Cargado'),
        ('synchronized', 'Sincronizado'),
        ('gen_fump', 'FUMP Registradas')
    ], string='Estado',
        default='draft',
        index=True,
        copy=False)
    header_row = fields.Text('Fila de Cabecera del Excel(JSON)')
    imported_fumps = fields.Integer('Cantidad de fump generados', index=True)
    synchronized_employees = fields.Integer('Empleados Sincronizados', index=True)
    synchronized_contract = fields.Integer('Contratos Sincronizados ', index=True)

    # Información del fichero importado
    total_rows = fields.Integer('Cantidad de filas', index=True)
    total_cols = fields.Integer('Cantidad de columnas', index=True)

    # Campos auxiliares para el manejo de errores
    fump_data_errors = fields.Boolean('Error en los datos de los fump', index=True)
    error_file_content = fields.Binary(string="Archivo", readonly=True)
    error_file_name = fields.Char(string="Archivo de errores", default="Archivo de errores", readonly=True, index=True)
    file_format = fields.Char(string='Formato del Archivo', index=True)

    fump_ids = fields.One2many('hr.fump', 'loader_id',
                               string="FUMPs")


    def action_load_file(self):
        """
        Se carga el Excel y se guarda en una tabla que se leerá posteriormente para la generación de los fump.
        """
        IrAttachment = self.env['ir.attachment']
        self.ensure_one()

        try:
            if self.state == 'draft':
                xls_attachment_file = IrAttachment.sudo().search([
                    ('res_model', '=', self._name),
                    ('res_field', '=', 'file'),
                    ('res_id', '=', self.sudo().id),
                ])
            else:
                xls_attachment_file = IrAttachment.sudo().search([
                    ('res_model', '=', self._name),
                    ('res_field', '=', 'fump_file'),
                    ('res_id', '=', self.sudo().id),
                ])

            xls_file_path = xls_attachment_file._full_path(xls_attachment_file.store_fname)
            xlrd_wb = xlrd.open_workbook(filename=xls_file_path)
        except Exception as e:
            raise UserError(_('El documento no es válido!'))

        self.validate_file(xlrd_wb)
        self.save_big_data(xlrd_wb)
        if self.state == 'draft':
            self.state = 'xlsx_loaded'
        elif self.state == 'synchronized':
            query = """
                        SELECT COUNT(1) FROM hr_fump WHERE loader_id=%s;
                    """
            self.env.cr.execute(query, (self.sudo().id,))
            self.imported_fumps = self.env.cr.fetchone()[0]
            self.state = ''
            self.state = 'gen_fump'

    @api.model
    def validate_file(self, workbook):
        if workbook.nsheets == 0:
            raise UserError(_('El fichero está vacío!'))

    def _read_xls_book(self, book, sheet):
        for row in map(sheet.row, range(sheet.nrows)):
            values = []
            for cell in row:
                if cell.ctype is xlrd.XL_CELL_NUMBER:
                    is_float = cell.value % 1 != 0.0
                    values.append(
                        str(cell.value)
                        if is_float
                        else str(int(cell.value))
                    )
                elif cell.ctype is xlrd.XL_CELL_DATE:
                    is_datetime = cell.value % 1 != 0.0
                    # emulate xldate_as_datetime for pre-0.9.3
                    dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value, book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        if is_datetime
                        else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elif cell.ctype is xlrd.XL_CELL_BOOLEAN:
                    values.append(u'True' if cell.value else u'False')
                elif cell.ctype is xlrd.XL_CELL_ERROR:
                    raise ValueError(
                        _("Error cell found while reading XLS/XLSX file: %s") %
                        xlrd.error_text_from_code.get(
                            cell.value, "unknown error code %s" % cell.value)
                    )
                else:
                    values.append(cell.value)
            if any(x for x in values if x.strip()):
                yield values

    def save_big_data(self, workbook):
        """
        Se cargan los datos del Excel en la tabla que se utilizará como big data.
        """
        self.ensure_one()

        list_sheet = []

        sheet = workbook.sheet_by_index(0)
        sheet_1 = workbook.sheet_by_index(1)

        list_sheet.append(sheet)
        list_sheet.append(sheet_1)

        for sheet in list_sheet:
            values = self._read_xls_book(workbook, sheet)

            try:
                pl_matrix = [row for row in values]
            except Exception as e:
                raise ValidationError(
                    _('%s valor inválido en la hoja %s' % (e, sheet.name)))

            if self.state == 'draft':

                self.header_row = json.dumps([str(el).split('.')[0] for el in pl_matrix[0]])

                callback = psycopg2.extensions.get_wait_callback()
                psycopg2.extensions.set_wait_callback(None)

                try:
                    content = u'\n'.join(
                        (u"%d\t" + (u"%s\t" * 49) + u"%s") % (
                            self.sudo().id,  # Para ubicar los registros del Big Data que corresponan a este asistente
                            *(str((row[i]) if row[i] else '\\N') for i in range(1, 32)),
                            *(str((row[i]) if row[i] else '\\N') for i in range(34, 47)),
                            *(str((row[i]) if row[i] else '\\N') for i in range(48, sheet.ncols))
                            , sheet.name
                        )
                        for row in pl_matrix[1:]
                    )

                    self.env.cr.copy_from(
                        io.StringIO(content),
                        table='hr_fump_xlsx_raw_data',
                        columns=BIG_DATA_FIELDS,
                    )
                finally:
                    psycopg2.extensions.set_wait_callback(callback)

            elif self.state == 'synchronized':
                self.action_generate_fump(pl_matrix)


    def remove_accentuation(self, value):
        replacements = (
            ("á", "a"),
            ("é", "e"),
            ("í", "i"),
            ("ó", "o"),
            ("ú", "u"),
            ("ü", "u"),
        )
        for a, b in replacements:
            value = value.replace(a, b).replace(a.upper(), b.upper())
        return value

    def get_valid_name(self, dict_by_name):
        name_data = {}
        for key in dict_by_name.keys():
            if key:
                new_key = (''.join(filter(str.isalnum, key))).replace(" ", "")
                new_key = self.remove_accentuation(new_key)
                name_data[new_key.upper()] = dict_by_name.get(key)

        return name_data

    def get_valid_value_name(self, value):
        valid_value = False
        if value:
            valid_value = (''.join(filter(str.isalnum, value))).replace(" ", "")
            valid_value = self.remove_accentuation(valid_value)
        return valid_value

    def action_sync_up(self):
        user_id = self.env.user.id
        create_date = fields.Date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        country_id = self.env['res.country'].search([('code', '=', 'MX')], limit=1)

        where_clause = None

        employee_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.employee',
            'name',
            ['id', 'l10n_mx_rfc', 'address_home_id'],
            where_clause
        )

        employees_name_data = self.get_valid_name(employee_by_name)

        contract_by_employee = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.contract',
            'employee_id',
            ['id', 'name', 'department_id', 'wage', 'job_id', 'date_start',
             'state', 'date_end'],
            where_clause
        )

        contract_query = """
                            SELECT
                                employee_id, id, name, job_id, department_id, date_start, state
                            FROM
                                hr_contract
                            WHERE
                                active = True                            
                        """
        self.env.cr.execute(contract_query)

        contract_by_employee = defaultdict(list)

        for cq in self.env.cr.fetchall():
            key = (
                cq[0],
                datetime.datetime.strftime(cq[5],'%Y-%m-%d')
            )
            contract_by_employee[key].append((cq[0],cq[1],cq[2],cq[3],cq[4],cq[5],cq[6]))


        # contract_data_emp_date = {}
        #
        # for key in contract_by_employee.keys():
        #     if key:
        #         new_key = (key, datetime.datetime.strftime(contract_by_employee.get(key)[7], '%Y-%m-%d'))
        #         contract_data_emp_date[new_key] = contract_by_employee.get(key)

        job_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.job',
            'name',
            ['id'],
            where_clause
        )

        job_name_data = self.get_valid_name(job_by_name)

        department_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.department',
            'name',
            ['id'],
            where_clause
        )

        department_name_data = self.get_valid_name(department_by_name)

        state_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'res.country.state',
            'name',
            ['id'],
            where_clause
        )

        state_name_data = self.get_valid_name(state_by_name)

        bank_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'res.partner.bank',
            'acc_number',
            ['id'],
            where_clause
        )

        bank_name_data = self.get_valid_name(bank_by_name)

        struct_by_id = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.payroll.structure',
            'id',
            ['name'],
            where_clause
        )

        where_cr_clause = """origin.active = True"""

        cr_by_code = loader_tools.get_mapped_data(
            self.env.cr,
            'account.analytic.account',
            'code',
            ['id', 'name'],
            where_cr_clause
        )

        where_cc_clause = """origin.active = True"""

        cc_by_id = loader_tools.get_mapped_data(
            self.env.cr,
            'account.analytic.account',
            'id',
            ['code', 'name'],
            where_cc_clause
        )

        list_error = []

        big_data_query = """
                                SELECT
                                    employee_rfc
                                FROM
                                    hr_fump_xlsx_raw_data
                                WHERE
                                    loader_id = %s and employee_rfc is not null
                                GROUP BY employee_rfc
                                HAVING COUNT(*) > 1
                            """
        self.env.cr.execute(big_data_query, (self.id,))
        list_rfc_xlsx = [v[0] for v in self.env.cr.fetchall()]

        if list_rfc_xlsx:
            big_data_query = """
                                SELECT
                                    l10n_mx_rfc
                                FROM
                                    hr_employee                            
                                WHERE l10n_mx_rfc in %s                          
                            """
            self.env.cr.execute(big_data_query, (tuple(set(list_rfc_xlsx)),))
            list_rfc = [v[0] for v in self.env.cr.fetchall()]

            diff_rfc = list(set(list_rfc_xlsx).difference(list_rfc))

            if diff_rfc:
                big_data_query = """                
                                   DELETE FROM
                                       hr_fump_xlsx_raw_data                
                                   WHERE
                                       employee_rfc in %s              
                                   """
                self.env.cr.execute(big_data_query, (tuple(diff_rfc),))
                list_error.append(
                    'Las lineas en el excel con los valores RFC: %s, fueron eliminadas de la sincronización para evitar empleados con RFC duplicados' % ', '.join(
                        diff_rfc))

        big_data_query = """
                            SELECT
                                l10n_mx_rfc, l10n_mx_curp
                            FROM
                                hr_employee 
                            WHERE l10n_mx_curp is not null and l10n_mx_rfc is not null;                                
                            """
        self.env.cr.execute(big_data_query)
        all_values = self.env.cr.fetchall()
        list_rfc_emp = [v[0] for v in all_values]
        list_curp_emp = [v[1] for v in all_values]
        if list_rfc_emp and list_curp_emp:
            big_data_query = """
                                SELECT
                                    employee_curp
                                FROM
                                    hr_fump_xlsx_raw_data                            
                                WHERE employee_curp in %s and employee_rfc not in %s                       
                            """
            self.env.cr.execute(big_data_query, (tuple(set(list_curp_emp)), tuple(set(list_rfc_emp))))
            list_curp = [v[0] for v in self.env.cr.fetchall()]
        else:
            list_curp = False

        if list_curp:
            big_data_query = """                
                               DELETE FROM
                                   hr_fump_xlsx_raw_data                
                               WHERE
                                   employee_curp in %s              
                               """
            self.env.cr.execute(big_data_query, (tuple(list_curp),))
            list_error.append(
                'Las lineas en el excel con los valores CURP: %s, fueron eliminadas de la sincronización para evitar empleados con CURP duplicados' % ', '.join(
                    list_curp))

        # Cargando las registros desde el Big Data:
        big_data_query = """
                    SELECT
                        %s
                    FROM
                        hr_fump_xlsx_raw_data
                    WHERE
                        loader_id = %s
                """ % (', '.join(BIG_DATA_FIELDS), self.id)
        self.env.cr.execute(big_data_query)

        parsed_contract = []
        parsed_resource = []

        rows_update_employee = []
        rows_update_contract = []
        rows_update_address = []

        values = self.env.cr.fetchall()
        counter = count(1)

        for slip_data in values:
            row_index = next(counter)
            sheet_name = slip_data[50]
            employee_rfc = slip_data[27]

            if employee_rfc and len(employee_rfc) > 13:
                list_error.append('Solo se permiten hasta 13 caracteres para el valor del RFC %s' % str(employee_rfc))
                continue

            lastname2 = slip_data[6]

            if not lastname2:
                list_error.append('Se requiere un Apellido Materno en la columna %s!' % str(row_index))
                continue

            lastname = slip_data[5]

            if not lastname:
                list_error.append('Se requiere un Apellido Paterno en la columna %s!' % str(row_index)
                                  )
                continue

            firstname = slip_data[4]

            if not firstname:
                list_error.append('Se requiere un Nombre en la columna %s!' % str(row_index))
                continue

            name = firstname + ' ' + lastname + ' ' + lastname2

            employee_name = self.get_valid_value_name(name)

            if employee_name:
                employee = employees_name_data.get(str(employee_name.upper()), False)
            else:
                employee = False

            l10n_mx_cfdi_rfc = employee_rfc
            l10n_mx_cfdi_curp = slip_data[28]

            if l10n_mx_cfdi_curp and len(l10n_mx_cfdi_curp) > 18:
                list_error.append(
                    'Solo se permiten hasta 18 caracteres para el valor del CURP %s' % str(l10n_mx_cfdi_curp))
                continue

            gender_value = self.get_valid_value_name(slip_data[26])
            if gender_value and gender_dicc.get(gender_value.upper(), False):
                gender = gender_dicc[gender_value.upper()]
            else:
                gender = '\\N'

            marital_value = self.get_valid_value_name(slip_data[44])
            if marital_value and marital_dicc.get(marital_value.upper(), False):
                marital = marital_dicc[marital_value.upper()]
            else:
                marital = '\\N'

            birthday = slip_data[31]
            if slip_data[35] and slip_data[36]:
                place_of_birth = slip_data[35] + ', ' + slip_data[36]
            else:
                place_of_birth = slip_data[35] or slip_data[36]

            ssnid = slip_data[30]

            job_name = self.get_valid_value_name(slip_data[14])
            message_job = slip_data[14]
            if job_name:
                job = job_name_data.get(str(job_name).upper(), False)
            else:
                job = False

            if job:
                job_id = str(job[0])
            else:
                job_id = False

            department_name = self.get_valid_value_name(slip_data[13])
            if department_name:
                department = department_name_data.get(str(department_name).upper(), False)
            else:
                department = False

            if department:
                department_id = str(department[0])
                cr_id = department[1] or False
                cc_id = department[2] or False
            else:
                department_id = False
                cr_id = False
                cc_id = False

            contract_date_start = slip_data[7]
            contract_date_end_1 = slip_data[8]
            contract_reentry_date_1 = slip_data[9]
            contract_date_end_2 = slip_data[10]
            contract_reentry_date_2 = slip_data[11]
            contract_date_end_3 = slip_data[12]

            column_wage = (slip_data[18].strip() if slip_data[18] else False)
            if column_wage:
                thousand_separator, decimal_separator = self.env['base_import.import']._infer_separators(column_wage, {})
                column_wage = column_wage.replace(thousand_separator, '').replace(decimal_separator, '.')
                column_wage = self.env['base_import.import']._remove_currency_symbol(column_wage)
                wage = float(column_wage)
            else:
                wage = 0.00

            state_value = slip_data[2]
            if state_value == 'BAJA':
                state = 'close'
            else:
                state = 'open'

            study_field = slip_data[46]

            if slip_data[37] and slip_data[38]:
                street = slip_data[37] + ' ' + slip_data[38]
            else:
                street = slip_data[37] or slip_data[38]
            street2 = slip_data[39]
            email = slip_data[34]
            colony = slip_data[40]
            zip = slip_data[43]
            state_address_value = self.get_valid_value_name(slip_data[42])
            if state_address_value:
                state_address = state_name_data.get(state_address_value.upper(), False)
            else:
                state_address = False

            certificate = slip_data[45]

            bank_value = slip_data[24]
            if bank_value:
                bank_account = bank_name_data.get(bank_value.upper(), False)
            else:
                bank_account = False

            employee_country = slip_data[29]
            age = slip_data[32]
            carnet_id = slip_data[47]



            #identifier_job = slip_data[15]

            if not employee:
                parsed_resource.append(
                    (
                        name,
                        'user',
                        100.00,
                        self.env.user.company_id.resource_calendar_id.id,
                        (self.env.user.tz or 'UTC'),
                        True,
                        self.env.user.company_id.id,
                        self.env.user.id,
                        fields.Date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                        self.id,
                        row_index,
                        self.id,
                    )
                )

            else:
                employee_id = employee[0]

                address_home_id = employee[2]

                rows_update_address.append({
                    'address_id': address_home_id,
                    'name': name,
                    'country_id': (country_id.id if country_id else None),
                    'street': street or None,
                    'street2': street2 or None,
                    #'l10n_mx_cfdi_colony': colony or None,
                    'zip': zip or None,
                    'state_id': (state_address[0] if state_address else None),
                    'active': True,
                    'company_id': self.env.user.company_id.id,
                    'type': 'private',
                    'employee': True,
                    'tz': (self.env.user.tz or 'UTC'),
                    'lang': 'es_MX',
                    'display_name': name,
                    'email': email,
                    'sync_up_id':self.id,
                })

                rows_update_employee.append({
                    'employee_id': employee_id,
                    'name': name,
                    'lastname2': lastname2,
                    'lastname': lastname,
                    'firstname': firstname,
                    'l10n_mx_rfc': l10n_mx_cfdi_rfc,
                    'l10n_mx_curp': l10n_mx_cfdi_curp,
                    'gender': gender,
                    'marital': marital,
                    'birthday': birthday,
                    'place_of_birth': place_of_birth,
                    'ssnid': ssnid,
                    'study_field': study_field,
                    'job_id': job_id or None,
                    'department_id': department_id or None,
                    'certificate': certificate or None,
                    'bank_account_id': (bank_account[0] if bank_account else None),
                    'country_id': (
                        country_id.id if country_id and employee_country and employee_country.upper() == 'MEXICANA' else None),
                    'carnet_id': carnet_id or None,
                    'sync_up': True,
                    'excel_row_index': row_index,
                    'address_id': self.env.user.company_id.partner_id.id,
                    'sync_up_id': self.id,
                })

                first_contract = contract_by_employee.get((employee[0],contract_date_start), False)
                contract_reentry_1 = contract_by_employee.get((employee[0], contract_reentry_date_1), False)
                contract_reentry_2 = contract_by_employee.get((employee[0], contract_reentry_date_2), False)
                list_contract = [first_contract,contract_reentry_1,contract_reentry_2]
                for contract in list_contract:
                    if contract:
                        current_state = contract[0][9]
                        current_date_start = contract[0][8]
                        if current_state == 'close':
                            if (current_date_start == contract_date_start and not contract_reentry_date_1) or (
                                    current_date_start == contract_reentry_date_1 and not contract_reentry_date_2) or (
                                    current_date_start == contract_reentry_date_2 and not contract_reentry_date_3):
                                current_state = state
                        ur_type = False
                        if ur:
                            ur_type = (''.join(filter(str.isalnum, ur[0].split('-')[1]))).replace(" ", "")
                        if (
                                ur_type and ur_type == 'H' and sheet_name.upper() == 'HONORARIOS' or ur_type == 'S' and sheet_name.upper() == 'SUELDO') or not ur_type:

                            rows_update_contract.append({
                                'contract_id': contract[0][1],
                                'name': name,
                                'wage': wage,
                                'state': (current_state if current_state != '\\N' else None),
                                'date_start':current_date_start,
                                'date_end': None,
                                'job_id': job_id or None,
                                'department_id': department_id or None,
                                #'type_id':type_id,
                                #'struct_id':struct_id,
                                'sync_up_id': self.id,
                            })

                            # if contract_reentry_date_2:
                            #     rows_update_contract[-1].update(date_start=contract_reentry_date_2)
                            #     current_contract_date = contract_reentry_date_2
                            # if contract_reentry_date_1 and not contract_reentry_date_2:
                            #     rows_update_contract[-1].update(date_start=contract_reentry_date_1)
                            #     current_contract_date = contract_reentry_date_1
                            # if not contract_reentry_date_1 and not contract_reentry_date_2 and contract_date_start:
                            #     rows_update_contract[-1].update(date_start=contract_date_start)
                            #     current_contract_date = contract_date_start

                            if current_state == 'close':
                                if current_date_start == fields.Date.from_string(contract_reentry_date_2) and contract_date_end_3:
                                    rows_update_contract[-1].update(date_end=contract_date_end_3)

                                if current_date_start == fields.Date.from_string(contract_reentry_date_1) and contract_date_end_2 and not contract_date_end_3:
                                    rows_update_contract[-1].update(date_end=contract_date_end_2)

                                if current_date_start == fields.Date.from_string(contract_date_start) and contract_date_end_1:
                                    rows_update_contract[-1].update(date_end=contract_date_end_1)

                employee_id = employee[0]

                if not job:
                    list_error.append(
                        'El puesto de trabajo con nombre %s no se encuentra en el sistema!' % message_job)
                    continue

                if not department:
                    list_error.append(
                        'El departamento con nombre %s no se encuentra en el sistema!' % slip_data[13])
                    continue


                if not contract_date_start:
                    list_error.append('Es necesaria una fecha de alta en fila %s' % row_index)

                current_contract_date_start = (first_contract[0][8].strftime(DEFAULT_SERVER_DATE_FORMAT) if first_contract else False)
                if contract_date_start and current_contract_date_start != contract_date_start and not first_contract:
                    parsed_contract.append(
                        (
                            name,
                            employee_id,
                            department_id or '\\N',
                            job_id or '\\N',
                            contract_date_start,  # date_start
                            (contract_date_end_1 if contract_date_end_1 else '\\N'),  # date_end
                            wage,
                            ('close' if contract_date_end_1 and contract_date_end_1 != '\\N' else state),
                            True,  # active,
                            user_id,  # create_uid
                            create_date,
                            self.id,
                            self.env.user.company_id.resource_calendar_id.id,
                            self.env.user.company_id.id,
                            (cr_id if cr_id else '\\N'),
                            (cc_id if cc_id else '\\N'),
                            self.id,
                        )
                    )

                if contract_reentry_date_1 and current_contract_date_start != contract_reentry_date_1 and not contract_reentry_1:
                    parsed_contract.append(
                        (
                            name,
                            employee_id,
                            department_id or '\\N',
                            job_id or '\\N',
                            contract_reentry_date_1,  # date_start
                            (contract_date_end_2 if contract_date_end_2 else '\\N'),  # date_end
                            wage,
                            ('close' if contract_date_end_2 else state),
                            True,  # active,
                            user_id,  # create_uid
                            create_date,
                            self.id,
                            self.env.user.company_id.resource_calendar_id.id,
                            self.env.user.company_id.id,
                            (str(cr_id) if cr_id else '\\N'),
                            (str(cc_id) if cc_id else '\\N'),
                            self.id,
                        )
                    )

                if contract_reentry_date_2 and current_contract_date_start != contract_reentry_date_2 and not contract_reentry_2:
                    parsed_contract.append(
                        (
                            name,
                            employee_id,
                            department_id or '\\N',
                            job_id or '\\N',
                            contract_reentry_date_2,  # date_start
                            (contract_date_end_3 if contract_date_end_3 else '\\N'),  # date_end
                            wage,
                            ('close' if contract_date_end_3 else state),
                            True,  # active,
                            user_id,  # create_uid
                            create_date,
                            self.id,
                            self.env.user.company_id.resource_calendar_id.id,
                            self.env.user.company_id.id,
                            (str(cr_id) if cr_id else '\\N'),
                            (str(cc_id) if cc_id else '\\N'),
                            self.id
                        )
                    )

        if list_error:
            callback = psycopg2.extensions.get_wait_callback()
            psycopg2.extensions.set_wait_callback(None)
            try:
                content = u'\n'.join(
                    u"%d\t%s" % (self.id, error_val)
                    for error_val in list_error
                )
                self.env.cr.copy_from(
                    io.StringIO(content),
                    table='hr_fump_import_error',
                    columns=['loader_id', 'name'],
                )
            finally:
                psycopg2.extensions.set_wait_callback(callback)

            self.fump_data_errors = True

        try:
            self.create_employee(
                parsed_resource,
                values,
                state_name_data,
                country_id,
                bank_name_data,
                job_name_data,
                department_name_data,
                cr_by_code,
                cc_by_id,
                struct_by_id
            )
            self.create_contract(parsed_contract)
            self.update_employee(rows_update_employee, rows_update_address)
            self.update_contract(rows_update_contract)
        except Exception as e:
            raise ValidationError(_(e))

        self.state = 'synchronized'

        query = """
                    SELECT COUNT(1) FROM hr_employee WHERE sync_up_loader_id=%s or sync_up_id = %s;
                """
        self.env.cr.execute(query, (self.id,self.id))
        self.synchronized_employees = self.env.cr.fetchone()[0]

        query = """
                    SELECT COUNT(1) FROM hr_contract WHERE sync_up_loader_id=%s or sync_up_id = %s;
                """
        self.env.cr.execute(query, (self.id,self.id))
        self.synchronized_contract = self.env.cr.fetchone()[0]

    def create_employee(self, parsed_resource, values, state_name_data, country_id, bank_name_data, job_name_data,
                        department_name_data, cr_by_code, cc_by_id, struct_by_id):

        user_id = self.env.user.id
        create_date = fields.Date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = u"%s\t%s\t%f\t%d\t%s\t%d\t%d\t%d\t%s\t%d\t%d\t%d"
        try:
            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_resource
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='resource_resource',
                columns=RESOURCE_RESOURCE_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        query = """
                    SELECT 
                        id, excel_row_index
                    FROM 
                        resource_resource                        
                    WHERE 
                        sync_up_loader_id=%s
                    ;
                """
        self.env.cr.execute(query, (self.id,))
        imported_resource = self.env.cr.fetchall()

        parsed_partners = []
        list_error = []

        for resource in imported_resource:
            resorce_lines_data = values[resource[1] - 1]

            row_index = resource[1]

            lastname2 = resorce_lines_data[6]

            if not lastname2:
                list_error.append('Se requiere un Apellido Materno en la fila %s!' % str(row_index))
                continue

            lastname = resorce_lines_data[5]

            if not lastname:
                list_error.append('Se requiere un Apellido Paterno en la fila %s!' % str(row_index)
                                  )
                continue

            firstname = resorce_lines_data[4]

            if not firstname:
                list_error.append('Se requiere un Apellido Paterno en la fila %s!' % str(row_index))
                continue

            name = firstname + ' ' + lastname + ' ' + lastname2

            if resorce_lines_data[37] and resorce_lines_data[38]:
                street = resorce_lines_data[37] + ' ' + resorce_lines_data[38]
            else:
                street = resorce_lines_data[37] or resorce_lines_data[38]

            street2 = resorce_lines_data[39]
            colony = resorce_lines_data[40]
            zip = resorce_lines_data[43]
            state_address_value = self.get_valid_value_name(resorce_lines_data[42])

            if state_address_value:
                state_address = state_name_data.get(state_address_value.upper(), False)
            else:
                state_address = False

            email = resorce_lines_data[34] or '\\N'

            parsed_partners.append(
                (
                    name,
                    (str(country_id.id) if country_id else '\\N'),
                    (street or '\\N'),
                    (street2 or '\\N'),
                    (colony or '\\N'),
                    (zip or '\\N'),
                    (str(state_address[0]) if state_address else '\\N'),
                    email,
                    True,
                    self.env.user.company_id.id,
                    'private',
                    False,
                    True,
                    True,
                    (self.env.user.tz or 'UTC'),
                    'es_MX',
                    name,
                    user_id,
                    create_date,
                    row_index,
                    self.id
                )
            )

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = (u"%s\t" + (u"%s\t" * 7) + u"%d\t%d\t%s\t%d\t%d\t%d\t%s\t%s\t%s\t%d\t%s\t%d\t%d")
        try:
            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_partners
            )

            self.env.cr.copy_from(
                io.StringIO(content),
                table='res_partner',
                columns=RES_PARTNER_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        parsed_employees = []

        where_address_clause = """ origin.excel_row_index is not null and origin.active = True """

        address_by_row_index = loader_tools.get_mapped_data(
            self.env.cr,
            'res.partner',
            'excel_row_index',
            ['id'],
            where_address_clause
        )

        for resource in imported_resource:

            resorce_lines_data = values[resource[1] - 1]

            row_index = resource[1]

            employee_rfc = resorce_lines_data[27]

            if employee_rfc and len(employee_rfc) > 13:
                list_error.append('Solo se permiten hasta 13 caracteres para el valor del RFC %s' % str(employee_rfc))
                continue

            lastname2 = resorce_lines_data[6]

            if not lastname2:
                list_error.append('Se requiere un Apellido Materno en la columna %s!' % str(row_index))
                continue

            lastname = resorce_lines_data[5]

            if not lastname:
                list_error.append('Se requiere un Apellido Paterno en la columna %s!' % str(row_index)
                                  )
                continue

            firstname = resorce_lines_data[4]

            if not firstname:
                list_error.append('Se requiere un Nombre en la columna %s!' % str(row_index))
                continue

            name = firstname + ' ' + lastname + ' ' + lastname2

            l10n_mx_cfdi_rfc = employee_rfc
            l10n_mx_cfdi_curp = resorce_lines_data[28]

            if l10n_mx_cfdi_curp and len(l10n_mx_cfdi_curp) > 18:
                list_error.append(
                    'Solo se permiten hasta 18 caracteres para el valor del CURP %s' % str(l10n_mx_cfdi_curp))
                continue

            gender_value = self.get_valid_value_name(resorce_lines_data[26])
            if gender_value and gender_dicc.get(gender_value.upper(), False):
                gender = gender_dicc[gender_value.upper()]
            else:
                gender = '\\N'

            marital_value = self.get_valid_value_name(resorce_lines_data[44])
            if marital_value and marital_dicc.get(marital_value.upper(), False):
                marital = marital_dicc[marital_value.upper()]
            else:
                marital = '\\N'

            birthday = resorce_lines_data[31] or '\\N'

            if resorce_lines_data[35] and resorce_lines_data[36]:
                place_of_birth = resorce_lines_data[35] + ', ' + resorce_lines_data[36]
            else:
                place_of_birth = resorce_lines_data[35] or resorce_lines_data[36]

            ssnid = resorce_lines_data[30] or '\\N'

            job_name = self.get_valid_value_name(resorce_lines_data[14])
            message_job = resorce_lines_data[14]
            if job_name:
                job = job_name_data.get(str(job_name).upper(), False)
            else:
                job = False

            if job:
                job_id = str(job[0])
            else:
                job_id = '\\N'

            department_name = self.get_valid_value_name(resorce_lines_data[13])
            if department_name:
                department = department_name_data.get(str(department_name).upper(), False)
            else:
                department = False

            if department:
                department_id = str(department[0])
            else:
                department_id = '\\N'

            study_field = resorce_lines_data[46] or '\\N'
            certificate = resorce_lines_data[45] or '\\N'

            bank_value = resorce_lines_data[24]
            if bank_value:
                bank_account = bank_name_data.get(bank_value.upper(), False)
            else:
                bank_account = False

            employee_country = resorce_lines_data[29] or '\\N'
            age = resorce_lines_data[32] or '\\N'
            carnet_id = resorce_lines_data[47] or '\\N'

            address_home = address_by_row_index.get(row_index, False)
            address_home_id = (str(address_home[0]) if address_home else '\\N')

            parsed_employees.append(
                (
                    name,
                    lastname2,
                    lastname,
                    firstname,
                    l10n_mx_cfdi_rfc,
                    l10n_mx_cfdi_curp,
                    gender,
                    marital,
                    birthday,
                    place_of_birth,
                    ssnid,
                    study_field,
                    job_id,
                    department_id,
                    address_home_id,
                    self.env.user.company_id.partner_id.id,
                    resource[0],
                    True,
                    self.env.user.company_id.id,
                    certificate,
                    self.env.user.company_id.resource_calendar_id.id,
                    (str(bank_account[0]) if bank_account else '\\N'),
                    (
                        str(country_id.id) if country_id and employee_country and employee_country.upper() == 'MEXICANA' else '\\N'),
                    carnet_id,
                    user_id,
                    create_date,
                    self.id,
                    row_index,
                    self.id,
                )
            )

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = (u"%s\t" + (u"%s\t" * 14) + u"%d\t%d\t%d\t%d\t%s\t%d\t%s\t%s\t%s\t%d\t%s\t%d\t%d\t%s")
        try:
            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_employees
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='hr_employee',
                columns=HR_EMPLOYEE_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        query = """
                    SELECT 
                        id, l10n_mx_rfc, excel_row_index
                    FROM 
                        hr_employee                        
                    WHERE 
                        sync_up_loader_id=%s
                    ;
                """
        self.env.cr.execute(query, (self.id,))
        imported_employee = self.env.cr.fetchall()

        parsed_contract = []

        for employee in imported_employee:
            employee_lines_data = values[employee[2] - 1]
            sheet_name = employee_lines_data[50]

            name = employee_lines_data[3]
            employee_id = employee[0]

            job_name = self.get_valid_value_name(employee_lines_data[14])
            message_job = employee_lines_data[14]
            job = job_name_data.get(str(job_name).upper(), False)

            if job:
                job_id = str(job[0])
            else:
                list_error.append('El puesto de trabajo con nombre %s no se encuentra en el sistema!' % message_job)
                continue

            department_name = self.get_valid_value_name(employee_lines_data[13])
            department = department_name_data.get(str(department_name).upper(), False)

            if department:
                department_id = str(department[0])
                cr_id = department[1] or False
                cc_id = department[2] or False
            else:
                list_error.append('El departamento con nombre %s no se encuentra en el sistema!' % employee_lines_data[13])
                continue

            contract_date_start = employee_lines_data[7] or '\\N'
            contract_date_end_1 = employee_lines_data[8] or '\\N'
            contract_reentry_date_1 = employee_lines_data[9] or '\\N'
            contract_date_end_2 = employee_lines_data[10] or '\\N'
            contract_reentry_date_2 = employee_lines_data[11] or '\\N'
            contract_date_end_3 = employee_lines_data[12] or '\\N'

            column_wage_H = employee_lines_data[18].strip()
            thousand_separator, decimal_separator = self.env['base_import.import']._infer_separators(column_wage_H, {})
            column_wage_H = column_wage_H.replace(thousand_separator, '').replace(decimal_separator, '.')
            column_wage_H = self.env['base_import.import']._remove_currency_symbol(column_wage_H)
            if column_wage_H:
                wage = float(column_wage_H)
            else:
                wage = 0.00

            state_value = employee_lines_data[2]
            if state_value == 'BAJA':
                state = 'close'
            else:
                state = 'open'



            #identifier_job = employee_lines_data[15]

            # ?contract_date_start
            if contract_date_start != '\\N':
                parsed_contract.append(
                    (
                        name,
                        employee_id,
                        department_id,
                        job_id,
                        contract_date_start,  # date_start
                        (contract_date_end_1) if contract_date_end_1 else '\\N',  # date_end
                        wage,
                        ('close' if contract_date_end_1 and contract_date_end_1 != '\\N' else state),
                        True,  # active,
                        user_id,  # create_uid
                        create_date,
                        self.id,
                        self.env.user.company_id.resource_calendar_id.id,
                        self.env.user.company_id.id,
                        (str(cr_id) if cr_id else '\\N'),
                        (str(cc_id) if cc_id else '\\N'),
                        self.id,
                    )
                )
            else:
                list_error.append('Sin fecha de inicio para el contrato de %s!' % name)
            if contract_date_end_1 and contract_reentry_date_1 and contract_reentry_date_1 != '\\N':
                parsed_contract.append(
                    (
                        name,
                        employee_id,
                        department_id,
                        job_id,
                        contract_reentry_date_1,  # date_start
                        (contract_date_end_2) if contract_date_end_2 else '\\N',  # date_end
                        wage,
                        ('close' if contract_date_end_2 else state),
                        True,  # active,
                        user_id,  # create_uid
                        create_date,
                        self.id,
                        self.env.user.company_id.resource_calendar_id.id,
                        self.env.user.company_id.id,
                        (str(cr_id) if cr_id else '\\N'),
                        (str(cc_id) if cc_id else '\\N'),
                        self.id,
                    )
                )

            if contract_date_end_2 and contract_reentry_date_2 and contract_reentry_date_2 != '\\N':
                parsed_contract.append(
                    (
                        name,
                        employee_id,
                        department_id,
                        job_id,
                        contract_reentry_date_2,  # date_start
                        (contract_date_end_3) if contract_date_end_3 else '\\N',  # date_end
                        wage,
                        ('close' if contract_date_end_3 else state),
                        True,  # active,
                        user_id,  # create_uid
                        create_date,
                        self.id,
                        self.env.user.company_id.resource_calendar_id.id,
                        self.env.user.company_id.id,
                        (str(cr_id) if cr_id else '\\N'),
                        (str(cc_id) if cc_id else '\\N'),
                        self.id,
                    )
                )

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = u"%s\t" + (u"%s\t" * 8) + u"%f\t" + u"%s\t%s\t%d\t%d\t%s\t%d\t%d\t%s\t%s\t%d\t%s\t%s\t%d"

        try:

            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_contract
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='hr_contract',
                columns=HR_CONTRACT_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        if list_error:
            callback = psycopg2.extensions.get_wait_callback()
            psycopg2.extensions.set_wait_callback(None)
            try:
                content = u'\n'.join(
                    u"%d\t%s" % (self.id, error_val)
                    for error_val in list_error
                )
                self.env.cr.copy_from(
                    io.StringIO(content),
                    table='hr_fump_import_error',
                    columns=['loader_id', 'name'],
                )
            finally:
                psycopg2.extensions.set_wait_callback(callback)

            self.fump_data_errors = True

    def create_contract(self, parsed_contract):
        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = u"%s\t" + (u"%s\t" * 8) + u"%f\t" + u"%s\t%s\t%d\t%d\t%s\t%d\t%d\t%s\t%s\t%d\t%s\t%s\t%d"

        try:
            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_contract
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='hr_contract',
                columns=HR_CONTRACT_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

    def update_employee(self, rows_update_employee, rows_update_address):
        self.env.cr._obj.executemany(
            '''
                UPDATE hr_employee
                SET
                    name = %(name)s,
                    lastname2 = %(lastname2)s,
                    lastname = %(lastname)s,
                    firstname = %(firstname)s,
                    l10n_mx_rfc = %(l10n_mx_rfc)s,
                    l10n_mx_curp = %(l10n_mx_curp)s,
                    gender = %(gender)s,
                    marital = %(marital)s,
                    birthday = %(birthday)s,
                    place_of_birth = %(place_of_birth)s,
                    ssnid = %(ssnid)s,
                    study_field = %(study_field)s,
                    job_id = %(job_id)s,
                    department_id = %(department_id)s,
                    certificate = %(certificate)s,
                    bank_account_id = %(bank_account_id)s,
                    country_id = %(country_id)s,                    
                    carnet_id = %(carnet_id)s,
                    sync_up = TRUE,
                    sync_up_id = %(sync_up_id)s,
                    excel_row_index = %(excel_row_index)s,
                    address_id = %(address_id)s                    
                WHERE
                    id = %(employee_id)s
            ''',
            rows_update_employee
        )

        self.env.cr.commit()

        self.env.cr._obj.executemany(
            '''
                UPDATE res_partner
                SET
                    name = %(name)s,
                    country_id = %(country_id)s,
                    street = %(street)s,
                    street2 = %(street2)s,
                    zip = %(zip)s,
                    state_id = %(state_id)s,
                    active = %(active)s,
                    company_id = %(company_id)s,
                    type = %(type)s,
                    employee = %(employee)s,
                    tz = %(tz)s,
                    lang = %(lang)s,
                    display_name = %(display_name)s,
                    sync_up_id = %(sync_up_id)s
                WHERE
                    id = %(address_id)s
            ''',
            rows_update_address
        )

        self.env.cr.commit()

    def update_contract(self, rows_update_contract):
        self.env.cr._obj.executemany(
            '''
                UPDATE hr_contract 
                SET
                    name = %(name)s,                   
                    wage = %(wage)s,                    
                    state = %(state)s,
                    sync_up = TRUE,
                    sync_up_id = %(sync_up_id)s,
                    date_start = %(date_start)s,
                    date_end = %(date_end)s,                    
                    job_id = %(job_id)s,
                    department_id = %(department_id)s,                                                            
                    
                WHERE
                    id = %(contract_id)s
            ''',
            rows_update_contract
        )

        self.env.cr.commit()

    def _get_data_xls_grouping(self, pl_matrix):

        contract_name_data = defaultdict(list)
        counter = count(1)
        for row in pl_matrix[3:]:
            name_key = row[4] + ' ' + row[5] + ' ' + row[6]
            group_key = (
                row[2],
                name_key
            )
            if not contract_name_data.get(group_key, False):
                dict_check = {
                    'values': defaultdict(list),
                }
                contract_name_data[group_key].append(dict_check)

            for data in range(13, len(row) - 3, 4):
                group_index = next(counter)
                try:
                    if row[data] != '' or row[data + 1] != '' or row[data + 2] != '' or row[data + 3] != '':
                        contract_name_data[group_key][0]['values'][group_index] = dict(date_from=row[data],
                                                                                       date_to=row[data + 1],
                                                                                       job=row[data + 2],
                                                                                       department=row[data + 3])
                except Exception as e:
                    pass
        return contract_name_data

    def action_draft(self):
        self.action_unlink_imported_fump()
        self.state = 'draft'

    def action_loan_fump(self):
        self.action_load_file()

    def action_generate_fump(self, pl_matrix):
        """
        Se generan los fump cargadas en el Big Data.
        """
        self.ensure_one()

        user_id = self.env.user.id
        create_date = fields.Date.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        where_clause = """ origin.active = True"""

        contract_by_employee = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.contract',
            'employee_id',
            ['id', 'name', 'department_id', 'wage', 'job_id', 'date_start',
             'state', 'date_end'],
            where_clause
        )

        contract_emp_data = {}

        for key in contract_by_employee.keys():
            if key:
                date_end_value = contract_by_employee.get(key)[7]
                date_end = (datetime.datetime.strftime(date_end_value, '%Y-%m-%d') if date_end_value else False)
                if 'datetime.date' in str(type(contract_by_employee.get(key)[7])):
                    new_key = (key, datetime.datetime.strftime(contract_by_employee.get(key)[7], '%Y-%m-%d'), date_end)
                    contract_emp_data[new_key] = contract_by_employee.get(key)

        employee_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.employee',
            'name',
            ['carnet_id', 'certificate', 'ssnid', 'sinid', 'l10n_mx_rfc', 'l10n_mx_curp', 'name', 'gender',
             'marital', 'place_of_birth', 'id'],
            where_clause
        )

        employees_name_data = self.get_valid_name(employee_by_name)

        movement_type_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.fump.movement.type',
            'name',
            ['id'],
            where_clause
        )

        movement_type_name_data = self.get_valid_name(movement_type_by_name)

        department_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.department',
            'name',
            ['name', 'id'],
            where_clause
        )

        department_name_data = self.get_valid_name(department_by_name)

        job_by_name = loader_tools.get_mapped_data(
            self.env.cr,
            'hr.job',
            'name',
            ['name', 'id'],
            where_clause
        )

        job_name_data = self.get_valid_name(job_by_name)

        contract_data = self._get_data_xls_grouping(pl_matrix)

        parsed_fump = []
        list_errors = []

        res_update_contract_department = []
        res_update_contract_job = []

        res_update_employee_department = []
        res_update_employee_job = []

        for slip_data, data in contract_data.items():
            values = data[0]['values']
            if values:
                employee_name = self.get_valid_value_name(slip_data[1])
                employee_state = slip_data[0]

                employee = employees_name_data.get(str(employee_name).upper(), False)

                if not employee:
                    list_errors.append('No existe el empleado: %s' % slip_data[1])
                    continue

                employee_carnet = employee[0] or '\\N'
                certificate = employee[1] or '\\N'
                ssnid = employee[2] or '\\N'
                sinid = employee[3] or '\\N'
                employee_filiation = employee[4] or '\\N'
                employee_curp = employee[5] or '\\N'
                employee_name = employee[6] or '\\N'
                gender = employee[7] or '\\N'
                marital = employee[8] or '\\N'
                place_of_birth = employee[9] or '\\N'

                employee_id = employee[10]

                last_key = False
                dict_contract_job_department = defaultdict(dict)
                dict_employee_job_department = defaultdict(dict)

                for key, value in values.items():
                    if value['date_from']:
                        date_from = value['date_from']
                    else:
                        date_from = '\\N'
                    if value['date_to']:
                        date_to = value['date_to']
                    else:
                        date_to = '\\N'
                    if value['job']:
                        job = value['job']
                    else:
                        job = '\\N'
                    if value['department']:
                        department_name = value['department']
                    else:
                        department_name = '\\N'

                    if last_key:
                        if values[last_key]['job']:
                            previous_job = values[last_key]['job']
                        else:
                            previous_job = '\\N'
                        if values[last_key]['department']:
                            previous_department = values[last_key]['department']
                        else:
                            previous_department = '\\N'
                    else:
                        previous_job = job
                        previous_department = department_name

                    department_id = False
                    if department_name:
                        valid_department_name = self.get_valid_value_name(department_name)
                        department = department_name_data.get(str(valid_department_name).upper(), False)
                        if department:
                            department_id = department[1]

                    job_id = False
                    if job:
                        valid_job_name = self.get_valid_value_name(job)
                        job_object = job_name_data.get(str(valid_job_name).upper(), False)
                        if job_object:
                            job_id = job_object[1]

                    # contract_key = (employee_id,value['date_from'],value['date_to'])

                    # contract = contract_emp_data.get(contract_key, False)

                    try:
                        datetime.datetime.strptime(date_from, "%d/%m/%Y").date()
                    except ValueError:
                        date_from = '\\N'
                    if date_to not in '\\N' and date_from not in '\\N':
                        clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]

                        clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]

                        clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False),
                                    ('date_end', '>=', date_to)]
                        clause_final = [('employee_id', '=', employee_id), '|',
                                        '|'] + clause_1 + clause_2 + clause_3

                    else:
                        if date_from not in '\\N':
                            clause_3 = ['&', ('date_start', '<=', date_from), ('date_end', '=', False)]
                        else:
                            clause_3 = ['&', ('date_start', '<=', False), ('date_end', '=', False)]
                        clause_final = [('employee_id', '=', employee_id)] + clause_3

                    contract = self.env['hr.contract'].search(clause_final, limit=1)

                    if not contract:
                        list_errors.append('No existe un contrato para el empleado: %s' % employee_name)
                        continue

                    contract_id = contract.id
                    contract_name = contract.name

                    wage = contract.wage

                    valid_employee_state = self.get_valid_value_name(employee_state)
                    movement_type = movement_type_name_data.get(str(valid_employee_state).upper(), False)

                    if not movement_type:
                        list_errors.append(
                            'No existe el tipo de movimiento de personal con nombre: %s' % employee_state)
                        continue

                    movement_type_id = movement_type[0]

                    ttyme = datetime.datetime.combine(fields.Date.from_string(date_from), datetime.time.min)
                    locale = self.env.context.get('lang') or 'en_US'
                    name = (_('FUMP of %s for %s') % (
                        contract_name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale))))

                    parsed_fump.append(
                        (
                            name,  # name
                            date_from,  # date_expedition
                            date_from,  # date_from
                            date_to,  # date_to
                            employee_id,  # employee_id
                            contract_id,  # contract_id
                            movement_type_id,  # movement_type_id
                            (department_id if department_id else '\\N'),  # department_id
                            employee_carnet,
                            certificate,
                            ssnid,
                            sinid,
                            employee_filiation,
                            employee_curp,
                            employee_name,
                            gender,
                            marital,
                            place_of_birth,
                            job,
                            wage,
                            wage,  # previous_salary
                            previous_job,  # previous_job
                            (department[0] if department else '\\N'),
                            previous_department,  # previous_department
                            self.sudo().id,
                            user_id,  # create_uid
                            create_date,  # create_date
                            self.env.user.sudo().company_id.id,

                        )
                    )
                    last_key = key

                    contract_department_id = contract.department_id.id
                    contract_job_id = contract.job_id.id

                    cont_emp_department_id = contract.employee_id.department_id.id
                    cont_emp_job_id = contract.employee_id.job_id.id

                    key = (contract.id)
                    employee_key = (contract.employee_id.id)
                    if key in dict_contract_job_department:
                        if ('job_id' in dict_contract_job_department[key] and dict_contract_job_department[key]['job_id'] != job_id) or ('job_id'not in dict_contract_job_department[key] and job_id):
                            dict_contract_job_department[key]['job_id'] = job_id
                        if ('department_id' in dict_contract_job_department[key] and dict_contract_job_department[key]['department_id'] != department_id) or ('department_id' not in dict_contract_job_department[key] and department_id):
                            dict_contract_job_department[key]['department_id'] = department_id
                    else:
                        dict_contract_job_department[key] = {'contract_department_id':contract_department_id,
                                                             'contract_job_id':contract_job_id}
                        if job_id:
                            dict_contract_job_department[key].update(job_id=job_id)
                        if department_id:
                            dict_contract_job_department[key].update(department_id=department_id)

                    if employee_key in dict_employee_job_department:
                        if 'job_id' in dict_employee_job_department[employee_key] and dict_employee_job_department[employee_key][
                            'job_id'] != job_id or ('job_id' not in dict_employee_job_department[employee_key] and job_id):
                            dict_employee_job_department[employee_key]['job_id'] = job_id
                        if ('department_id' in dict_employee_job_department and dict_employee_job_department[employee_key][
                            'department_id'] != department_id) or ('department_id' not in dict_employee_job_department[employee_key] and department_id):
                            dict_employee_job_department[employee_key]['department_id'] = department_id
                    else:
                        dict_employee_job_department[employee_key] = {'cont_emp_department_id': cont_emp_department_id,
                                                                      'cont_emp_job_id': cont_emp_job_id}
                        if job_id:
                            dict_employee_job_department[employee_key].update(job_id=job_id)
                        if department_id:
                            dict_employee_job_department[employee_key].update(department_id=department_id)

                for contract_id, data_values in dict_contract_job_department.items():
                    if 'job_id' in data_values and data_values['contract_job_id'] != data_values['job_id']:
                        res_update_contract_job.append({'job_id': data_values['job_id'],'contract_id':contract_id})
                    if 'department_id' in data_values and data_values['contract_department_id'] != data_values['department_id']:
                        res_update_contract_department.append({'department_id': data_values['department_id'],'contract_id':contract_id})
                for employee_id, data_values in dict_employee_job_department.items():
                    if 'job_id' in data_values and data_values['cont_emp_job_id'] != data_values['job_id']:
                        res_update_employee_job.append({'job_id': data_values['job_id'],'employee_id':employee_id})
                    if 'department_id' in data_values and data_values['cont_emp_department_id'] != data_values['department_id']:
                        res_update_employee_department.append({'department_id': data_values['department_id'],'employee_id':employee_id})

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        str_transform = u"%s\t" + (u"%s\t" * 3) + (u"%d\t" * 3) + (u"%s\t" * 13) + (
                u"%f\t" * 2) + (u"%s\t" * 3) + (u"%d\t" * 2) + u"%s\t" + u"%d"
        try:

            content = u'\n'.join(
                str_transform %
                ps_data
                for ps_data in parsed_fump
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='hr_fump',
                columns=FUMP_FIELDS,
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        callback = psycopg2.extensions.get_wait_callback()
        psycopg2.extensions.set_wait_callback(None)
        try:
            content = u'\n'.join(
                u"%d\t%s" % (self.id, error_val)
                for error_val in list_errors
            )
            self.env.cr.copy_from(
                io.StringIO(content),
                table='hr_fump_import_error',
                columns=['loader_id', 'name'],
            )
        finally:
            psycopg2.extensions.set_wait_callback(callback)

        if list_errors:
            self.fump_data_errors = True

        if res_update_contract_department:
            self.env.cr._obj.executemany(
                '''
                    UPDATE hr_contract 
                    SET
                        department_id = %(department_id)s
                    WHERE
                        id = %(contract_id)s
                ''',
                res_update_contract_department
            )

            self.env.cr.commit()

        if res_update_employee_department:
            self.env.cr._obj.executemany(
                '''
                    UPDATE hr_employee
                    SET
                        department_id = %(department_id)s
                    WHERE
                        id = %(employee_id)s
                ''',
                res_update_employee_department
            )

            self.env.cr.commit()

        if res_update_contract_job:
            self.env.cr._obj.executemany(
                '''
                    UPDATE hr_contract 
                    SET
                        job_id = %(job_id)s
                    WHERE
                        id = %(contract_id)s
                ''',
                res_update_contract_job
            )

            self.env.cr.commit()

        if res_update_employee_job:
            self.env.cr._obj.executemany(
                '''
                    UPDATE hr_employee 
                    SET
                        job_id = %(job_id)s
                    WHERE
                        id = %(employee_id)s
                ''',
                res_update_employee_job
            )

            self.env.cr.commit()

    def action_view_imported_fumps(self):
        self.ensure_one()

        query = """
            SELECT id FROM hr_fump WHERE loader_id=%s;
        """
        self.env.cr.execute(query, (self.id,))
        imported_fumps = [ps[0] for ps in self.env.cr.fetchall()]

        action = {
            'name': _('FUMP importados'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.fump',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', imported_fumps)],
        }

        return action

    def action_view_synchronized_employees(self):
        self.ensure_one()

        query = """
            SELECT id FROM hr_employee WHERE sync_up_loader_id=%s or sync_up_id = %s;
        """
        self.env.cr.execute(query, (self.id,self.id))
        synchronized_employees = [ps[0] for ps in self.env.cr.fetchall()]

        action = {
            'name': _('Empleados Sincronizados'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', synchronized_employees)],
        }

        return action

    def action_view_synchronized_contracts(self):
        self.ensure_one()

        query = """
            SELECT id FROM hr_contract WHERE sync_up_loader_id=%s or sync_up_id = %s;
        """
        self.env.cr.execute(query, (self.id,self.id))
        synchronized_contract = [ps[0] for ps in self.env.cr.fetchall()]

        action = {
            'name': _('Contratos Sincronizados'),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.contract',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('id', 'in', synchronized_contract)],
        }

        return action

    def action_unlink_imported_only_fump(self):
        query = """
                    WITH to_delete AS (
                        SELECT id FROM hr_fump WHERE loader_id=%s
                    )
                    DELETE FROM
                        hr_fump
                    USING
                        to_delete
                    WHERE
                        hr_fump.id = to_delete.id
                    ;
                """
        self.env.cr.execute(query, (self.id,))

        self.imported_fumps = 0

    def action_unlink_imported_fump(self):
        """
        La eliminación de los registros cargados se realizan a bajo nivel por el volumen de información a eliminar.
        """

        self.ensure_one()

        query = """
            WITH to_delete AS (
                SELECT id FROM hr_fump_xlsx_raw_data WHERE loader_id=%s
            )
            DELETE FROM
                hr_fump_xlsx_raw_data
            USING
                to_delete
            WHERE
                hr_fump_xlsx_raw_data.id = to_delete.id
            ;
        """
        self.env.cr.execute(query, (self.id,))

        query = """
            SELECT id FROM hr_fump WHERE loader_id=%s;
        """
        self.env.cr.execute(query, (self.id,))
        fump_to_unlink = [ps[0] for ps in self.env.cr.fetchall()]

        if fump_to_unlink:
            hr_fump = self.env['hr.fump'].browse(fump_to_unlink)
            hr_fump.unlink()

        # Empleados
        query = """
                    SELECT id FROM hr_employee WHERE sync_up_loader_id=%s;
                """
        self.env.cr.execute(query, (self.id,))
        employee_to_unlink = [ps[0] for ps in self.env.cr.fetchall()]

        if employee_to_unlink:
            hr_employee = self.env['hr.employee'].browse(employee_to_unlink)
            hr_employee.unlink()

        # Contratos
        query = """
                    SELECT id FROM hr_contract WHERE sync_up_loader_id=%s;
                """
        self.env.cr.execute(query, (self.id,))
        contract_to_unlink = [ps[0] for ps in self.env.cr.fetchall()]

        if contract_to_unlink:
            hr_contract = self.env['hr.contract'].browse(contract_to_unlink)
            hr_contract.unlink()

        if self.fump_data_errors:
            query = """
                WITH to_delete AS (
                    SELECT id FROM hr_fump_import_error WHERE loader_id = %s
                )
                DELETE FROM
                    hr_fump_import_error
                USING
                    to_delete
                WHERE
                    hr_fump_import_error.id = to_delete.id
                ;
            """
            self.env.cr.execute(query, (self.id,))

        self.fump_data_errors = False
        self.error_file_content = False
        self.error_file_name = False
        self.imported_fumps = 0
        self.state = 'draft'

        return {'type': 'ir.actions.act_window_close'}

    def action_view_import_errors(self):
        self.ensure_one()

        action = {
            'name': _('Errores de importación: %s' % self.sudo().name),
            'type': 'ir.actions.act_window',
            'res_model': 'hr.fump.import.error',
            'view_mode': 'tree,form',
            'target': 'current',
            'domain': [('loader_id', '=', self.sudo().id)],
        }
        return action

class RemittanceImportError(models.Model):
    _name = 'hr.fump.import.error'

    loader_id = fields.Many2one('hr.fump.loader', ondelete='cascade', index=True)
    name = fields.Char('Nombre', index=True)

class SynchronizationXlsxBigData(models.Model):
    _name = 'hr.fump.xlsx.raw.data'
    _order = 'no_employee'

    # Excel kardex Sueldos y Honorarios.xlsx
    loader_id = fields.Integer(index=True)
    no_employee = fields.Char()  # columna B
    employee_status = fields.Char()  # columna C
    employee_full_name = fields.Char()  # columna D
    employee_firstname = fields.Char()  # columna E
    employee_lastname = fields.Char()  # columna F
    employee_lastname2 = fields.Char()  # columna G
    contract_date_start = fields.Char()  # columna H
    contract_date_end_1 = fields.Char()  # columna I
    contract_reentry_date_1 = fields.Char()  # columna J
    contract_date_end_2 = fields.Char()  # columna K
    contract_reentry_date_2 = fields.Char()  # columna L
    contract_date_end_3 = fields.Char()  # columna M

    department = fields.Char()  # columna N Me sirve para UR
    job = fields.Char()  # columna O
    id_job_in_contract = fields.Char()  # columna P

    # Datos del tabulador que hay revisar
    nivel = fields.Char()  # columna Q
    tabulator = fields.Char()  # columna R

    salary = fields.Char()  # columna S
    pantry = fields.Char()  # columna T
    passage = fields.Char()  # columna U
    monthly_gross_salary = fields.Char()  # columna V

    period_type = fields.Char()  # columna W
    payment_method = fields.Char()  # columna X
    banck_account = fields.Char()  # columna Y
    account = fields.Char()  # columna Z
    employee_gender = fields.Char()  # columna AA
    employee_rfc = fields.Char()  # columna AB
    employee_curp = fields.Char()  # columna AC
    employee_country = fields.Char()  # columna AD
    employee_ssnid = fields.Char()  # columna AE
    employee_birthdate = fields.Char()  # columna AF
    employee_age = fields.Char()  # columna AI
    employee_phone = fields.Char()  # columna AJ
    employee_mun_of_birth = fields.Char()  # columna AL
    employee_est_of_birth = fields.Char()  # columna AM

    # Datos de la direccion privada

    employee_email = fields.Char()  # columna AK
    employee_street = fields.Char()  # columna AN
    employee_ext_no = fields.Char()  # columna AO—
    employee_int_no = fields.Char()  # columna AP
    employee_colony = fields.Char()  # columna AQ
    employee_municipality = fields.Char()  # columna AR
    employee_state = fields.Char()  # columna AS
    employee_cp = fields.Char()  # columna AT

    employee_marital = fields.Char()  # columna AU
    employee_certificate = fields.Char()  # columna AW
    employee_study_field = fields.Char()  # columna AX
    employee_carnet = fields.Char()  # columna AY

    withdrawal_reason = fields.Char()  # columna AZ (Motivo de la ultima baja)
    employee_bloodtype_factor = fields.Char()  # columna BA

    sheet_name = fields.Char()  # Nombre de la hoja necesario para encontrar la Unidad Responsable