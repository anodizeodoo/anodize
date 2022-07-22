# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from __future__ import division

import base64
import logging
import re
import time
from io import BytesIO
from itertools import groupby
from calendar import monthrange
import requests

from lxml import etree, objectify
from werkzeug import url_encode
from zeep import Client
from zeep.transports import Transport

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError, UserError
from odoo.tools import DEFAULT_SERVER_TIME_FORMAT
from odoo.tools.xml_utils import _check_with_xsd

_logger = logging.getLogger(__name__)


class L10nMxPayrollEmployerRegistration(models.Model):
    _name = 'l10n_mx_payroll.employer.registration'
    _description = 'Allow define all the employer registration from the company'
    _inherit = ['mail.thread']

    name = fields.Char(
        help='Value to set in the "RegistroPatronal" attribute.')
    job_risk_id = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.', required=True)

class HrEmployee(models.Model):
    _inherit = "hr.employee"

    l10n_mx_edi_syndicated = fields.Boolean(
        'Syndicated', help='Used in the XML to indicate if the worker is '
        'associated with a union. If it is omitted, it is assumed that it is '
        'not associated with any union.')
    l10n_mx_edi_risk_rank = fields.Many2one(
        'l10n_mx_edi.job.risk', 'Job Risk',
        help='Used in the XML to express the key according to the Class in '
        'which the employers must register, according to the activities '
        'carried out by their workers, as provided in article 196 of the '
        'Regulation on Affiliation Classification of Companies, Collection '
        'and Inspection, or in accordance with the regulations Of the Social '
        'Security Institute of the worker.')
    l10n_mx_edi_contract_regime_type_id = fields.Many2one('l10n.mx.edi.contract.regime.type', string='Regime Type')
    l10n_mx_edi_is_assimilated = fields.Boolean(
        'Is assimilated?', help='If this employee is assimilated, must be '
        'used this option, to get the correct rules on their payslips')
    l10n_mx_edi_employer_registration_id = fields.Many2one(
        'l10n_mx_payroll.employer.registration', 'Employer Registration',
        help='If the company has multiple employer registration, define the '
        'correct for this employee.')
    l10n_mx_edi_rfc = fields.Char(related='address_home_id.vat', string='RFC', readonly=False, store=True)
    l10n_mx_edi_curp = fields.Char(related='address_home_id.l10n_mx_edi_curp', string='CURP', readonly=False, store=True)
    l10n_mx_edi_family_medical_unit = fields.Char(string='Family Medical Unit')
    l10n_mx_edi_afore_number = fields.Char(string='Afore Number')
    l10n_mx_payment_method = fields.Selection([('PUE', '(PUE) Pago en una sola exhibición'),
                                               ('PPD', '(PPD) Pago en parcialidades o diferido')],
                                               default='PUE', string="Payment method")