from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    expiration_date = fields.Date(string='Expiration Date')
    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    package_type = fields.Many2one('package.type', string="Package Type")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope",
                                        domain=[('type', '=', 'sea')])
    shipment_scope_id_in = fields.Many2one('shipment.scop', string="Shipment Scope",
                                           domain=[('type', '=', 'inland')])
    container_type = fields.Many2one('container.type', string="Container Type")
    package_type_1 = fields.Many2one('package.type', string="Package Type")
    pol_id = fields.Many2one(comodel_name='port.cites', string='POL')
    pod_id = fields.Many2one(comodel_name='port.cites', string='POD')
    transit_time_dur = fields.Integer(string='Transit Time Duration')
    free_time_dur = fields.Integer(string='Free Time Duration')
    shipping_line = fields.Many2one(comodel_name="res.partner", string="Shipping Line",
                                    domain="[('partner_type_id.name', '=', 'Shipping Line'), ('is_company', '=', True)]")
    air_line = fields.Many2one(comodel_name="res.partner", string="Air Line",
                               domain="[('partner_type_id.name', '=', 'Air Line'), ('is_company', '=', True)]")
    trucker = fields.Many2one(comodel_name="res.partner", string="Trucker",
                              domain="[('partner_type_id.name', '=', 'Trucker'), ('is_company', '=', True)]")
    commodity_id = fields.Many2one('commodity.data', string='Commodity')
    commodity_equip = fields.Selection(
        string='Commodity Equip',
        selection=[('dry', 'Dry'),
                   ('imo', 'IMO'),
                   ('reefer', 'Reefer'),
                   ])
    temperature = fields.Float(string="Temperature", required=False)
    un_number = fields.Char('UN Number')
    attach_id = fields.Binary('Attachment')
    incoterms_id = fields.Many2one('account.incoterms', 'Incoterms')
    pickup = fields.Boolean(string="Pickup Address", related="incoterms_id.pickup")
    delivery = fields.Boolean(string="Delivery Address", related="incoterms_id.delivery")

    fixed_charges_ids = fields.One2many('product.charges', 'purchase_id', string='Charges')
    package_ids = fields.Many2many('air.package.type', string="Packages")
    lcl_container_type_ids = fields.Many2many('lcl.container.type',
                                              string="Lcl Container Types")
    ltl_container_type_ids = fields.Many2many('ltl.container.type',
                                              string="Lcl Container Types")
    fcl_container_type_ids = fields.Many2many('fcl.container.type',
                                              string="Fcl Container Types")
    ftl_container_type_ids = fields.Many2many('ftl.container.type',
                                              string="Ftl Container Types")
    price_req_id = fields.Many2one('request.price',string="Request Price")

    def action_open_price(self):
        return {
            'name': _('Create New Commodity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.price',
            'view_id': self.env.ref(
                'eit_freight_pricing.view_arequest_price').id,
            'res_id': self.price_req_id.id,
            'target': 'current',
        }

    @api.onchange('pol_id', 'pod_id')
    def onchange_pod(self):
        if self.pol_id and self.pod_id:
            if self.pol_id.id == self.pod_id.id:
                raise UserError(_('Please select another port.'
                                  'You cant choose the same port at two different locations.'))


class ProductCharges(models.Model):
    _name = 'product.charges'
    _description = "Product charges"

    product_id = fields.Many2one('product.template', string="Charge Type",
                                 domain="[('detailed_type', '=', 'charge_type')]")
    cost_price = fields.Float(string="Cost Price")
    qty = fields.Float(string="QTY")
    package_type = fields.Many2one('package.type', string="Package Type")

    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    tot_cost_fr = fields.Float(string="Total cost In System Currency", compute='_compute_tot_price')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    tot_cost = fields.Float(string="Total Cost in ( auto fill from Purchase currency)",
                            compute='_compute_tot_price')
    order_line = fields.Many2one('purchase.order.line')

    @api.model
    def create(self, values):
        res = super(ProductCharges, self).create(values)

        val = {
            'product_id': res.product_id.product_variant_id.id,
            'price_unit': res.cost_price,
            'product_qty': res.qty,
            'order_id': res.purchase_id.id,
        }
        order = self.env['purchase.order.line'].create(val)
        res.order_line = order.id

        return res

    @api.onchange('product_id', 'cost_price', 'qty')
    def onchange_qty(self):
        if self.order_line:
            self.order_line.product_id = self.product_id.product_variant_id.id
            self.order_line.price_unit = self.cost_price
            self.order_line.product_qty = self.qty

    @api.depends('cost_price', 'ex_rate', 'qty')
    def _compute_tot_price(self):
        for record in self:
            if record.cost_price and record.ex_rate and record.qty:
                record.tot_cost_fr = record.cost_price * record.ex_rate * record.qty
            else:
                record.tot_cost_fr = 0

            record.tot_cost = record.purchase_id.currency_id.rate * record.tot_cost_fr
