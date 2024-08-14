from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    is_default = fields.Boolean(string="Default for Projects", default=False)
