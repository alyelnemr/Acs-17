# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pricing_id = fields.Many2one(comodel_name='product.template', string="Source Pricing for this quotation")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")

    def action_view_pricing_id(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('id', '=', self.id)],
            'multi': False,
            'name': 'Pricing',
            'target': 'current',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
        }

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.opportunity_id:
            self.opportunity_id.action_set_won()
        return res

    def _action_cancel(self):
        res = super(SaleOrder, self)._action_cancel()
        if self.opportunity_id:
            opportunity_quotations = self.env['sale.order'].search([('opportunity_id', '=', self.opportunity_id.id)])
            if all(quot.state == 'cancel' for quot in opportunity_quotations):
                self.opportunity_id.action_set_lost()
        return res

    def create_operation(self, project_id=None):
        if not project_id:
            raise UserError('No project found for this customer. Please create a project first.')
        project_task_charge_ids = []
        for line in self.order_line:
            project_task_charge_ids.append((0, 0, {
                'product_id': line.product_id.id,
                'qty': line.product_uom_qty,
                'sale_price': line.price_unit,
                'currency_id': line.currency_id.id,
            }))

        task_vals = {
            'project_id': project_id.id,  # Example Project
            'transport_type_id': self.transport_type_id.id,  # Example of transport type
            'shipment_scope_id': self.shipment_scope_id.id,  # Example of Shipment Scope
            'port_id': self.pol.id,  # Example POL
            'port_id_pod': self.pod.id,  # Example POD
            'incoterm_id': self.incoterms.id,  # Example Incoterm
            'commodity_id': self.commodity.id,  # Example Commodity
            'sale_order_booking_id': self.id,
            'project_task_charge_ids': project_task_charge_ids,  # Add route lines
        }

        # Create the task
        task = self.env['project.task'].create(task_vals)

        self.project_task_id = task.id  # Set the task ID in the sale order

    def action_create_operation(self):
        # Prepare the data to create a project task
        project_id = self.env['project.project'].search([('partner_id', '=', self.partner_id.id)], limit=1)
        if not project_id:
            return {
                'name': 'Confirm Message',
                'type': 'ir.actions.act_window',
                'res_model': 'confirm.message.wizard',
                'view_mode': 'form',
                'context': {
                    'default_message': 'No profile found for this customer. Do you want to create a new profile?',
                    'default_confirm_message': self.partner_id.name,
                },
                'target': 'new',
            }
        else:
            self.create_operation(project_id=project_id)


    def action_view_project_task(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.task',
            'res_id': self.project_task_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
