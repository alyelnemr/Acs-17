from odoo import fields, models
from odoo.exceptions import UserError


class ContainerData(models.Model):
    _inherit = 'container.data'

    task_id_container = fields.Many2one('project.task')
    loading_instruction = fields.Html(string="Loading Instructions")
    is_save_container = fields.Boolean('Is Save Container?', store=True, default=True)

    def save_container(self):
        for record in self:
            if record.name and record.container_id and record.container_type:
                # Check if the container already exists
                container_exists = self.env['container.data'].search([('name', '=', record.name)], limit=1).id
                if not container_exists:
                    self.env['container.data'].create({
                        'name': record.name,
                        'container_id': record.container_id.id,
                        'container_type': record.container_type,
                        'is_save_container': False
                    })
                    record.write({'is_save_container': False})
                    self.env.cr.commit()

                # else:
                #     raise UserError('This container already exists.')
            else:
                raise UserError(
                    'Please fill in the container number, Container Type, and Container ID before saving the container data.')
