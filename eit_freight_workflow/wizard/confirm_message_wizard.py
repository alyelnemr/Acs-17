from odoo import api, fields, models
from odoo.addons.sale_purchase_inter_company_rules.models.sale_order import sale_order


class ConfirmMessageWizard(models.TransientModel):
    _name = 'confirm.message.wizard'
    _description = 'Confirmation Message Wizard'

    name = fields.Char(string="Title", default="Confirmation")
    message = fields.Char(string="Message", default="Are you sure you want to ?")
    confirm_message = fields.Char("")
    show_label = fields.Boolean(string="Show Label", default=True)

    def confirm_action(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            sale_order = self.env['sale.order'].browse(active_id)
            project_id = self.env['project.project'].create(
                {'partner_id': sale_order.partner_id.id, 'name': sale_order.partner_id.name,
                 'description': sale_order.partner_id.name})
            sale_order.create_operation(project_id)

    def action_mark_lost(self):
        action = self.env.ref('crm.crm_lead_lost_action').read()[0]
        active_id = self.env.context.get('active_id')
        if active_id:
            lead = self.env['crm.lead'].browse(active_id)
            action['context'] = {'default_lead_id': lead.id}
            # You can modify the context if needed, like passing active_ids or other parameters
            action['context'] = {
                'dialog_size': 'medium',
                'default_lead_ids': [active_id]  # Pass current record's ID or a list of IDs
            }
            return action