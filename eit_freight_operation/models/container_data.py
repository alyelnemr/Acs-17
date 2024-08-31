from odoo import fields, models, api


class ContainerData(models.Model):
    _inherit = 'container.data'

    shipping_container_ids = fields.One2many(comodel_name='shipping.container', inverse_name='container_id',
                                             string="Operations")
    project_task_ids = fields.One2many(comodel_name='project.task', string="Operations",
                                       compute='_compute_project_task_ids', store=False)
    project_task_count = fields.Integer(string="Project Task Count", compute='_compute_project_task_count', store=False)

    @api.depends('project_task_ids', 'shipping_container_ids')
    def _compute_project_task_count(self):
        for record in self:
            record.project_task_count = len(record.project_task_ids)

    @api.depends('shipping_container_ids')
    def _compute_project_task_ids(self):
        for record in self:
            # Get all project_task_ids from related shipping_container_ids
            project_task_ids = record.shipping_container_ids.mapped('project_task_id')
            record.project_task_ids = [(6, 0, project_task_ids.ids)]

    def action_view_project_tasks(self):
        """
        This method is triggered by the smart button. It returns an action to open the
        specific form view (view_project_task_inherit_form) if there is only one related
        project task, or the specified list view (project.open_view_all_tasks_list_view) if there are multiple tasks.
        """
        self.ensure_one()  # Ensure the method is called on a single record
        task_ids = self.project_task_ids.ids

        if len(task_ids) == 1:
            # Open the form view if there is only one project task
            action = {
                'name': 'Operations',
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'form',
                'views': [(self.env.ref('eit_freight_operation.view_project_task_inherit_form').id, 'form')],
                'res_id': task_ids[0],  # Open the single task directly
                'context': {'default_container_id': self.id},
            }
        else:
            # Open the list view if there are multiple project tasks
            action = {
                'name': 'Operations',
                'type': 'ir.actions.act_window',
                'res_model': 'project.task',
                'view_mode': 'tree,form',
                'views': [(self.env.ref('project.open_view_all_tasks_list_view').id, 'tree')],
                'domain': [('id', 'in', task_ids)],
                'context': {'default_container_id': self.id},
            }

        return action

