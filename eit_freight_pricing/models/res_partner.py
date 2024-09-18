from odoo import models, fields, api

class InheritResPartner(models.Model):
    _inherit = "res.partner"

    price_count = fields.Integer(string="Price Count", compute='get_price_count')

    def action_view_pricing(self):
        product_ids = self.env['product.template'].search([('partner_id', '=', self.id), ('detailed_type', '=', 'pricing')])

        if len(product_ids) == 1:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pricing',
                'view_mode': 'form',
                'res_model': 'product.template',
                'res_id': product_ids.id,  # Open the form view with the single record
                'view_id': self.env.ref('eit_freight_pricing.product_template_form_view_pricing2').id,
                'target': 'current',
                'context': {
                    'default_partner_id': self.id,
                    'default_detailed_type': 'pricing',
                },
            }
        else:
            # If more than one record, open the tree (list) view
            return {
                'type': 'ir.actions.act_window',
                'name': 'Pricing',
                'view_mode': 'tree,form',  # Show list view, and form when clicked
                'res_model': 'product.template',
                'domain': [('partner_id', '=', self.id), ('detailed_type', '=', 'pricing')],
                'view_id': self.env.ref('eit_freight_pricing.product_template_tree_view_pricing2').id,
                'context': {
                    'default_partner_id': self.id,
                    'default_detailed_type': 'pricing',
                },
                'target': 'current',
            }

    def get_price_count(self):
        for rec in self:
            count = self.env['product.template'].search_count([('partner_id', '=', self.id), ('detailed_type', '=', 'pricing')])
            rec.price_count = count
