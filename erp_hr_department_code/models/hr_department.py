
from odoo import api, fields, models


class Department(models.Model):
    _inherit = "hr.department"
    _order = "code, name"

    code = fields.Char(string='Code')

    def name_get(self):
        res = []
        for dep in self:
            name = dep.name
            if dep.code:
                name = ("[%(code)s] %(name)s") % {"code": dep.code, "name": name}
            res.append((dep.id, name))
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("code", operator, name), ("name", operator, name)]
        department = self.search(domain + args, limit=limit)
        return department.name_get()
