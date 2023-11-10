from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_sequence = fields.Boolean(string='Configuración de secuencia', default=False, index=True)

    employee_id_sequence = fields.Many2one(
        comodel_name="ir.sequence",
        string="Identificador de Secuencia",
        help="Patrón que se utilizará para la generación de identificadores de empleados",
        default=lambda self: self._default_id_sequence(),
    )

    def _default_id_sequence(self):
        sequence = self.env.user.company_id.employee_id_sequence
        if not sequence:
            sequence = self.env.ref("erp_hr_employee_sequence.erp_hr_seq_employee_number", raise_if_not_found=False)
        return sequence and sequence.id or False
