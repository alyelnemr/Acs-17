from odoo import models, fields, api
from datetime import date, timedelta

class ProjectTaskClosingWizard(models.TransientModel):
    _name = 'project.task.closing.wizard'
    _description = 'Project Task Closing Wizard'

    date_field = fields.Date(string='Date', required=True, default=lambda self: (date.today() + timedelta(days=30)).strftime('%Y-%m-%d'))

    def action_confirm(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            my_model = self.env['my.model'].browse(active_id)
            my_model.write({
                'date_field': self.date_field,  # Assuming 'date_field' is a field in 'my.model'
            })
        return {'type': 'ir.actions.act_window_close'}
