from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sale_order_booking_id = fields.Many2one(comodel_name='sale.order', string='Booking')

    def action_view_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_booking_id.id,
        }