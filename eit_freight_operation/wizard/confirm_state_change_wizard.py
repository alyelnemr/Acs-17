from odoo import api, fields, models


class ConfirmStateChangeWizard(models.TransientModel):
    _name = 'confirm.state.change.wizard'
    _description = 'Confirmation Wizard for State Change'

    message = fields.Char(string="Message", default="Are you sure you want to close this operation?")
    state = fields.Char("")

    def confirm_action(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            record = self.env['project.task'].browse(active_id)
            if record.state_selectable == '1_done':
                record.write({'state': '1_done', 'state_selectable': '1_done', 'stage_id': self.env.ref('eit_freight_operation.stage_closed').id})
