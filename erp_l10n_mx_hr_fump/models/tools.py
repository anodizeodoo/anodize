# -*- coding: utf-8 -*-

from odoo import _
import logging

from odoo.exceptions import UserError
from string import Template as StringTemplate

_logger = logging.getLogger(__name__)

SQL_OP = ['insert', 'delete', 'drop', 'join', 'create']


def perform_bash_insertion(cr, table_name, fields, values, return_ids=True):
    """
    Inserta varios elementos en un modelo, en una sola consulta(bash).
    :type table_name: char
    :type fields: list, tuple
    :param values: list of tuples containing the values
    :type values: list
    :return: New created records ids
    """

    validate_values(values)
    if isinstance(fields, list):
        fields = tuple(fields)

    if return_ids:
        base_query = 'INSERT INTO $table_name %s VALUES $values RETURNING id;' % str(fields).replace("'", '')
    else:
        base_query = 'INSERT INTO $table_name %s VALUES $values;' % str(fields).replace("'", '')

    query_template = StringTemplate(base_query)

    parsed_values = ", ".join([
        str(tuple([(isinstance(v, str) and ('null' in v)) and v.replace("'", '') or v for v in value]))
        for value in values
    ])
    # parsed_values.replace("'", '')
    parsed_values = parsed_values.replace("'null'", 'null')

    query = query_template.substitute(table_name=table_name, fields=fields, values=parsed_values)
    cr.execute(query)

    new_record_ids = []

    if return_ids:
        new_record_ids = [record[0] for record in cr.fetchall()]

    return new_record_ids


def validate_values(values):
    """
    Preventing sql injection
    """
    for value in values:
        if isinstance(value, str):
            for op in SQL_OP:
                if op in value.lower():
                    raise UserError(_('SQL INJECTION ALERT: The document contains SQL operations!'))


def split_values(x, n, decimals=2):
    decimals = decimals or 2
    result = []
    r = 0
    amount = x / n
    amount_rounded = round(amount, decimals)
    for i in range(n):
        r = r + amount - amount_rounded
        r_round = round(r, decimals)
        if i + 1 == n:
            result.append(round(amount_rounded + r_round, decimals))
        else:
            result.append(amount_rounded)
    return result

def get_mapped_data(cr, ref_model, key_field, fields_to_fetch,where_clause=None,join_model=None,join_clause=None):
    """
    Devuelve un diccionario con los campos del modelo leído.    """

    ref_model = ref_model.replace('.', '_')

    origin_fields_to_fetch = []
    for field in fields_to_fetch:
        origin_fields_to_fetch.append('origin.' + field)
    origin_fields_to_fetch.append('origin.' + key_field)

    query = "SELECT %s FROM %s origin" % (', '.join(origin_fields_to_fetch), ref_model)
    if join_model:
        join_model = join_model.replace('.', '_')
        query = query + " INNER JOIN" + ' ' + join_model + ' rel' + ' ON' + join_clause

    if where_clause:
        query = query + " WHERE %s" % (where_clause)

    query = query + ' ORDER BY id' + ";"

    cr.execute(query)
    fetched_values = cr.fetchall()

    data = {}
    for v in fetched_values:
        if isinstance(v[-1], str):
            if v[-1].upper() not in data:
                data[v[-1].upper()] = v
        else:
            if 'dict' not in str(type(v[-1])):
                if v[-1] not in data:
                    data[v[-1]] = v
    return data
