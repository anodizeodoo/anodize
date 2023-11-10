from odoo import fields, models, api


class Job(models.Model):
    _inherit = 'hr.job'

    code = fields.Char(string='Code')

    def name_get(self):
        res = []
        for job in self:
            name = job.name
            if job.code:
                name = ("[%(code)s] %(name)s") % {"code": job.code, "name": name}
            res.append((job.id, name))
        return res
