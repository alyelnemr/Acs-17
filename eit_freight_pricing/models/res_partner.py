from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    price_count = fields.Integer(string="Price Count", compute='get_price_count')

    def action_view_pricing(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('partner_id', '=', self.id), ('detailed_type', '=', 'pricing')],
            'multi': False,
            'name': 'Pricing',
            'target': 'current',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
        }
    
    def get_price_count(self):
        for rec in self:
            count = self.env['product.template'].search_count([('partner_id', '=', self.id), ('detailed_type', '=', 'pricing')])
            rec.price_count = count
