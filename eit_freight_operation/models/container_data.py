from odoo import fields, models


class ContainerData(models.Model):
    _inherit = 'container.data'

    task_id_container = fields.Many2one('project.task')
