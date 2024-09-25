from odoo import fields, models, api
from odoo.exceptions import UserError


class AvailablePrices(models.Model):
    _name = 'crm.available.prices'
    _description = 'CRM Available Prices'

    product_id = fields.Many2one(comodel_name='product.template', string="Pricing")
    pricing_name = fields.Char(string="Pricing Name", related='product_id.name')
    transport_type_id = fields.Many2one(comodel_name='transport.type', string="Transport Type",
                                        related='product_id.transport_type_id')
    shipment_scope_id = fields.Many2one(comodel_name='shipment.scop', string="Shipment Scope",
                                        related='product_id.shipment_scope_id')
    package_type_id = fields.Many2one(comodel_name='package.type', string="Package Type",
                                      related='product_id.package_type')
    container_type_id = fields.Many2one(comodel_name='container.type', string="Container Type",
                                        related='product_id.container_type')
    scope_ids = fields.Many2many(comodel_name='service.scope', string="Services", related='product_id.scope_ids')
    scope_names = fields.Char(string='Service Scopes', compute='_compute_scope_names', store=False)
    expiration_date = fields.Date(string="Expiration Date", related='product_id.expiration_date')
    pol_id = fields.Many2one(comodel_name='port.cites', string="POL", related='product_id.pol_id')
    pod_id = fields.Many2one(comodel_name='port.cites', string="POD", related='product_id.pod_id')
    transit_time_duration = fields.Integer(string="Transit Time", related='product_id.transit_time_duration')
    free_time_duration = fields.Integer(string="Free Time", related='product_id.free_time_duration')
    shipping_line_id = fields.Many2one(comodel_name='res.partner', string="Shipping Line", related='product_id.shipping_line')
    air_line_id = fields.Many2one(comodel_name='res.partner', string="Air Line", related='product_id.air_line')
    crm_lead_id = fields.Many2one(comodel_name='crm.lead', string="Opportunity")
    pricing_charge_ids = fields.One2many(comodel_name='pricing.charges', inverse_name='product_id',
                                         related='product_id.pricing_charge_ids')
    vessel_line_ids = fields.One2many(comodel_name='frieght.vessel.line', inverse_name='product_vessel_id',
                                      related='product_id.vessel_line_ids')
    plane_line_ids = fields.One2many(comodel_name='frieght.plane.line', inverse_name='product_plane_id',
                                     related='product_id.plane_line_ids')

    def _compute_scope_names(self):
        for record in self:
            if record.scope_ids:
                # Join scope names with commas
                record.scope_names = ', '.join(record.scope_ids.mapped('name'))
            else:
                record.scope_names = 'No Scopes Available'

    def action_create_quotation(self):
        self.ensure_one()  # Ensure this is called on a single record

        if not self.crm_lead_id.partner_id:
            raise UserError("There is no Customer defined to create a quotation.")

        if not self.crm_lead_id:
            raise UserError("There is no linked CRM Lead to create a quotation.")

        # Prepare values for the new Sale Order
        sale_order_values = {
            'partner_id': self.crm_lead_id.partner_id.id,  # Customer from CRM Lead
            'opportunity_id': self.crm_lead_id.id,
            'pricing_id': self.product_id.id,
            'pol': self.crm_lead_id.pol_id.id,
            'pod': self.crm_lead_id.pod_id.id,
            'commodity': self.crm_lead_id.commodity_id.id,
            'commodity_equip': self.crm_lead_id.commodity_equip,
            'incoterms': self.crm_lead_id.incoterms_id.id,
            'shipment_scope_id': self.crm_lead_id.shipment_scope_id.id,
            'transport_type_id': self.crm_lead_id.transport_type_id.id,
            # Map pricing_charge_ids to charges_ids in the Sale Order
            'order_line': [
                (0, 0, {
                    'product_id': charge.product_id.product_variant_ids[0].id,  # Charge Origin
                    'product_template_id': charge.product_id_2.id,  # Charge Type
                    'name': charge.product_id_2.name,  # Charge Type Name
                    'product_uom': charge.product_id_2.uom_id.id,  # Charge Type Unit of Measure
                    'price_unit': charge.sale_price,  # Sale price
                    'unit_rate': charge.sale_price,  # Sale price
                    'product_uom_qty': charge.qty,  # Quantity
                    'package_type': charge.package_type.id if charge.package_type else None,  # Package Type
                    'currency_id': charge.currency_id.id,  # Currency
                    'ex_rate': charge.ex_rate,  # Exchange Rate
                }) for charge in self.pricing_charge_ids
            ]
        }

        # Create a new Sale Order
        sale_order = self.env['sale.order'].create(sale_order_values)
        followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
        if not followup_stage:
            raise UserError("No Follow up stage found in the system. Please create one.")
        self.crm_lead_id.stage_id = followup_stage.id

        # Optionally, return an action to open the Sale Order form view
        return {
            'name': 'Sale Order',
            'view_mode': 'form',
            'res_model': 'sale.order',
            'view_id': self.env.ref('sale.view_order_form').id,  # Reference to the form view
            'type': 'ir.actions.act_window',
            'res_id': sale_order.id,  # Pass the newly created sale order ID
            'target': 'current',
        }
