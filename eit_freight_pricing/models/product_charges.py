from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ProductCharges(models.Model):
    _name = 'product.charges'
    _description = "Product Charges"

    product_id = fields.Many2one('product.template', string="Charge Type",
                                 domain="[('detailed_type', '=', 'charge_type')]")
    cost_price = fields.Float(string="Cost Price")
    qty = fields.Float(string="QTY")
    package_type = fields.Many2one('package.type', string="Package Type")
    container_type = fields.Many2one('container.type', string="Container Type")
    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    tot_cost_fr = fields.Float(string="Total cost In System Currency", compute='_compute_tot_price')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order')
    tot_cost = fields.Float(string="Tax Excl.(Main Currency)",
                            compute='_compute_tot_price')
    tot_cost_inc = fields.Float(string="Tax Incl. (Main Currency)",
                                compute='_compute_tot_cost_inc')
    tax_inc_usd = fields.Float(string="Tax Incl (USD))",
                               compute='_compute_tax_inc_usd')

    order_line = fields.Many2one('purchase.order.line')
    tax_id = fields.Many2many(
        comodel_name='account.tax',
        string="Taxes",
        store=True, readonly=False)

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

    @api.depends('tot_cost', 'tax_id')
    def _compute_tot_cost_inc(self):
        for record in self:
            taxes = sum(tax.amount for tax in record.tax_id)
            record.tot_cost_inc = record.tot_cost * (1 + taxes / 100)

    @api.depends('tot_cost_inc', 'ex_rate')
    def _compute_tax_inc_usd(self):
        for record in self:
            if record.ex_rate:
                currency_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
                if currency_id and currency_id.rate_ids:
                    company_rate = currency_id.rate_ids[0].company_rate if currency_id.rate_ids else 1.0
                    inverse_company_rate = currency_id.rate_ids[0].inverse_company_rate
                    record.tax_inc_usd = record.tot_cost_inc * company_rate
                else:
                    # Handle the case where there's no rate available
                    record.tax_inc_usd = 0
            else:
                record.tax_inc_usd = 0

    @api.model
    def unlink(self):
        PurchaseOrderLine = self.env['purchase.order.line']
        for fixed_charge in self:
            # Search for the corresponding purchase order line
            purchase_order_line = PurchaseOrderLine.search([
                ('order_id', '=', self.purchase_id.id),  # Assuming order_id is a common field
                ('product_id', '=', fixed_charge.product_id.product_variant_id.id),
                ('price_unit', '=', fixed_charge.cost_price * fixed_charge.ex_rate),
                ('price_subtotal', '=', fixed_charge.tot_cost),
                ('product_qty', '=', fixed_charge.qty),
            ])

            # Delete the corresponding purchase order line
            if purchase_order_line:
                purchase_order_line.unlink()

        # Delete the fixed charge line itself
        return super(ProductCharges, self).unlink()

    # @api.depends('qty', 'cost_price', 'currency_id')
    # def _compute_rate_per_currency(self):
    #     for record in self:
    #         rate_data = {}
    #         for line in record:
    #             currency = line.currency_id.id
    #             if currency not in rate_data:
    #                 rate_data[currency] = {'currency_id': currency.id, 'amount': 0}
    #             rate_data[currency]['amount'] += line.qty * line.cost_price

    #         record.rate_per_currency_ids = [(5, 0, 0)]  # Clear existing data
    #         for data in rate_data.values():
    #             record.rate_per_currency_ids = [(0, 0, data)]
