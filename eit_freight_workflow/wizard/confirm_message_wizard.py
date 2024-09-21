from odoo import api, fields, models
from odoo.addons.sale_purchase_inter_company_rules.models.sale_order import sale_order


class ConfirmMessageWizard(models.TransientModel):
    _name = 'confirm.message.wizard'
    _description = 'Confirmation Message Wizard'

    name = fields.Char(string="Title", default="Confirmation")
    message = fields.Char(string="Message", default="Are you sure you want to ?")
    confirm_message = fields.Char("")

    def confirm_action(self):
        active_id = self.env.context.get('active_id')
        if active_id:
            sale_order = self.env['sale.order'].browse(active_id)
            project_id = self.env['project.project'].create(
                {'partner_id': sale_order.partner_id.id, 'name': sale_order.partner_id.name,
                 'description': sale_order.partner_id.name})
            sale_order.create_operation(project_id)
