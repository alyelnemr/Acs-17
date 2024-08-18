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
    count_price_req = fields.Integer(string="Price Req Count", compute='get_request_price_count')
    scope_ids = fields.Many2many('service.scope', string="Services")
    rate_per_currency_ids = fields.One2many(
        comodel_name='charge.type.currency.rate',
        inverse_name='purchase_id',
        string="Rate Per Currency",
        compute='_compute_rate_per_currency',
        store=True
    )
    charge_amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_compute_untaxed_amount', tracking=True)

    fixed_charge_tax_details = fields.Text(
        string="Fixed Charge Tax Details",
        compute='_compute_fixed_charge_tax_details',
        readonly=True
    )

    # fixed_charge_tax_names = fields.Text(string='Tax Names', compute='_compute_fixed_charge_tax_details',)
    # fixed_charge_tax_amounts = fields.Text(string='Tax Amounts', compute='_compute_fixed_charge_tax_details',)

    total_cost_in_usd = fields.Float(string="Total Amount (USD", compute="_onchange_pricing_charge_ids")
    total_amount = fields.Monetary(
        string='Total Amount',
        store=True,
        readonly=True,
        compute='_compute_total_amount',
        currency_field='currency_id'
    )
    total_amount_usd = fields.Float(
        string='Total Amount (USD)',
        compute='_onchange_fixed_charges_ids',
        store=True,
        readonly=True,
    )

    subtotal_w_o_whtax = fields.Monetary(
        string='Subtotal W/O WHTax',
        compute='_compute_subtotal_w_o_whtax',
        store=True,
        readonly=True,
        currency_field='currency_id'
    )

    @api.depends('fixed_charges_ids')
    def _compute_subtotal_w_o_whtax(self):
        for order in self:
            positive_tax_totals = 0.0
            negative_tax_exists = False

            # Sum up positive taxes from fixed_charges_ids
            for line in order.fixed_charges_ids:
                if line.tax_id:
                    for tax in line.tax_id:
                        tax_amount = line.tot_cost * (tax.amount / 100)
                        if tax_amount > 0:
                            positive_tax_totals += tax_amount
                        elif tax_amount < 0:
                            negative_tax_exists = True

            if negative_tax_exists:
                order.subtotal_w_o_whtax = order.charge_amount_untaxed + positive_tax_totals
            else:
                order.subtotal_w_o_whtax = 0

    @api.onchange('fixed_charges_ids')
    def _onchange_fixed_charges_ids(self):
        # Force recompute if fixed charges are changed
        self._compute_subtotal_w_o_whtax()
    
    @api.depends('fixed_charges_ids')
    def _compute_fixed_charge_tax_details(self):
        for order in self:
            positive_tax_totals = {}
            negative_tax_totals = {}
            max_tax_name_length = 0

            # Sum up tax amounts for each tax name and determine the maximum length of tax names
            for line in order.fixed_charges_ids:
                if line.tax_id:
                    for tax in line.tax_id:
                        tax_amount = line.tot_cost * (tax.amount / 100)
                        
                        if tax.name not in positive_tax_totals:
                            positive_tax_totals[tax.name] = 0.0
                            negative_tax_totals[tax.name] = 0.0
                            max_tax_name_length = max(max_tax_name_length, len(tax.name))
                        
                        if tax_amount >= 0:
                            positive_tax_totals[tax.name] += tax_amount
                        else:
                            negative_tax_totals[tax.name] += tax_amount

            tax_details = []

            # Format positive tax totals
            for tax_name, tax_amount in positive_tax_totals.items():
                if tax_amount > 0:
                    currency_symbol = order.currency_id.symbol or ''
                    formatted_tax = f"{tax_name:<{max_tax_name_length}}: {tax_amount:>10.2f} {currency_symbol}"
                    tax_details.append(f"{formatted_tax}")

            # Format negative tax totals
            for tax_name, tax_amount in negative_tax_totals.items():
                if tax_amount < 0:
                    currency_symbol = order.currency_id.symbol or ''
                    formatted_tax = f"{tax_name:<{max_tax_name_length}}: {tax_amount:>10.2f} {currency_symbol}"
                    tax_details.append(f"{formatted_tax}")

            # Combine all the tax details into a single string
            order.fixed_charge_tax_details = "\n".join(tax_details) if tax_details else ""

    @api.model
    def create(self, vals):
        # Create the purchase order first
        order = super(PurchaseOrder, self).create(vals)

        for charge in order.fixed_charges_ids:
            if charge.product_id:
                self.order_line += self.env['purchase.order.line'].new({
                    'order_id': self.id,
                    'product_id': charge.product_id.product_variant_id.id,
                    'name': charge.product_id.product_variant_id.display_name,
                    'taxes_id': [(6, 0, charge.tax_id.ids)],
                    'price_unit': charge.cost_price * charge.ex_rate,
                    'product_qty': charge.qty,  # Set quantity as needed
                })
        
        # Now that we have an order ID, create the order lines based on fixed charges
        
        return order

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)
        
        for charge in self.fixed_charges_ids:
            if charge.product_id:
                # Find the corresponding order line based on the product
                existing_order_line = self.order_line.filtered(lambda l: l.product_id == charge.product_id.product_variant_id)
                
                if existing_order_line:
                    # Update the existing order line
                    existing_order_line.write({
                        'order_id': self.id,
                        'product_id': charge.product_id.product_variant_id.id,
                        'name': charge.product_id.product_variant_id.display_name,
                        'taxes_id': [(6, 0, charge.tax_id.ids)],
                        'price_unit': charge.cost_price * charge.ex_rate,
                        'product_qty': charge.qty,
                    })
                else:
                    # If no corresponding order line, create a new one
                    self.order_line.create({
                        'order_id': self.id,
                        'product_id': charge.product_id.product_variant_id.id,
                        'name': charge.product_id.product_variant_id.display_name,
                        'taxes_id': [(6, 0, charge.tax_id.ids)],
                        'price_unit': charge.cost_price * charge.ex_rate,
                        'product_qty': charge.qty,
                    })
        
        return result
    
    @api.depends('charge_amount_untaxed', 'fixed_charges_ids')
    def _compute_total_amount(self):
        for order in self:
            total_amount = order.charge_amount_untaxed
            positive_taxes = 0.0
            withholding_taxes = 0.0

            for line in order.fixed_charges_ids:
                if line.tax_id:
                    for tax in line.tax_id:
                        tax_amount = line.tot_cost * (tax.amount / 100)
                        if tax.amount > 0:
                            positive_taxes += tax_amount
                        else:
                            withholding_taxes += tax_amount

            # Calculate the total amount
            total_amount += positive_taxes - withholding_taxes

            # Ensure the total matches the "Total Tax Incl. (main curr.)" column
            # Assuming that you have a field for the total including tax
            order.total_amount = total_amount

    # def _create_order_lines_from_fixed_charges(self):
    #     self.ensure_one()
    #     order_line_obj = self.env['purchase.order.line']
    #     # Clear existing lines linked to fixed charges
    #     self.order_line = self.order_line.filtered(lambda l: l.product_id not in self.fixed_charges_ids.mapped('product_id.product_variant_id'))

    #     for charge in self.fixed_charges_ids:
    #         order_line_obj.create({
    #             'order_id': self.id,  # Now the order_id exists
    #             'product_id': charge.product_id.product_variant_id.id,
    #             'name': charge.product_id.product_variant_id.display_name,
    #             'taxes_id': [(6, 0, charge.tax_id.ids)],
    #             'price_unit': charge.cost_price * charge.ex_rate,
    #             'product_qty': charge.qty,  # Set quantity as needed
    #         })

    # @api.onchange('fixed_charges_ids')
    # def _onchange_fixed_charges(self):
    #     # Remove existing fixed charge lines from order lines
    #     self.order_line = self.order_line.filtered(lambda l: l.product_id not in self.fixed_charges_ids.mapped('product_id.product_variant_id'))

    #     # Create corresponding order lines for each fixed charge
    #     for charge in self.fixed_charges_ids:
    #         if charge.product_id:
    #             self.order_line += self.env['purchase.order.line'].new({
    #                 'order_id': self.id,
    #                 'product_id': charge.product_id.product_variant_id.id,
    #                 'name': charge.product_id.product_variant_id.display_name,
    #                 'taxes_id': [(6, 0, charge.tax_id.ids)],
    #                 'price_unit': charge.cost_price * charge.ex_rate,
    #                 'product_qty': charge.qty,  # Set quantity as needed
    #             })
    
    @api.depends('fixed_charges_ids')
    def _compute_untaxed_amount(self):
        for order in self:
            total = 0.0
            for line in order.fixed_charges_ids:
                total += line.tot_cost  # Replace with the actual field name for "Tax Excl. (Main Curr.)"
            order.charge_amount_untaxed = total
    
    
    @api.onchange('fixed_charges_ids')
    def compute_tot_cost(self):
        for rec in self:
            if rec.fixed_charges_ids:
                sale_list = [(5, 0, 0)]
                currency = rec.fixed_charges_ids.mapped('currency_id')
                for cur in currency:
                    amount = 0
                    for charg in rec.fixed_charges_ids:
                        if cur.id == charg.currency_id.id:
                            amount += charg.cost_price * charg.qty
                    val = {
                        'currency_id': cur,
                        'amount': amount
                    }
                    sale_list.append((0, 0, val))
                rec.update({'rate_per_currency_ids': sale_list})
            else:
                rec.rate_per_currency_ids = False

    # @api.model
    # def create(self, values):
    #     res = super(PurchaseOrder, self).create(values)
    #     for line in res.fixed_charges_ids:
    #         val = {
    #             'currency_id': line.currency_id.id,
    #             'amount': line.cost_price,
    #             'purchase_id': res.id,
    #             'charge_id': line.id,
    #             }
    #     self.env['charge.type.currency.rate'].create(val)
    #     # res.order_line = order.id

    #     return res

    # def write(self, values):
    #     # Call the super method to perform the standard write operation
    #     res = super(PurchaseOrder, self).write(values)

    #     # Iterate over the records in self
    #     for record in self:
    #         # Prepare the data for charge.type.currency.rate
    #         for line in record.fixed_charges_ids:
    #             val = {
    #                 'currency_id': line.currency_id.id,
    #                 'amount': line.cost_price * line.qty,
    #                 'purchase_id': record.id,
    #                 'charge_id': line.id,
    #             }

    #             # Check if a record already exists for the given purchase_id and charge_id
    #             existing_rate = self.env['charge.type.currency.rate'].search([
    #                 ('purchase_id', '=', record.id),
    #                 ('charge_id', '=', line.id)
    #             ], limit=1)

    #             if existing_rate:
    #                 # If a record exists, update it
    #                 existing_rate.write(val)
    #             else:
    #                 # Otherwise, create a new record
    #                 self.env['charge.type.currency.rate'].create(val)

    #     return res
    
    def get_request_price_count(self):
        for rec in self:
            count = self.env['request.price'].search_count([('id', '=', self.price_req_id.id)])
            rec.count_price_req = count

    def action_open_price(self):
        return {
            'name': _('Create New Commodity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'product.price',
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

    tot_amount_usd_display = fields.Char(
        string='Total Amount (USD) Display',
        compute='_compute_total_amount_usd_display',
        store=True,
        readonly=True,
    )

    @api.depends('fixed_charges_ids')
    def _onchange_fixed_charges_ids(self):
        self.total_amount_usd = sum(self.fixed_charges_ids.mapped('tax_inc_usd'))

    @api.depends('total_amount_usd')
    def _compute_total_amount_usd_display(self):
        for record in self:
            # Format the amount with the currency symbol after the number
            record.tot_amount_usd_display = "{:,.2f} $".format(record.total_amount_usd)


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
                currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
                inverse_company_rate = currency_id.rate_ids[0].inverse_company_rate
                record.tax_inc_usd = record.tot_cost_inc * inverse_company_rate
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


class ChargeTypeCurrencyRate(models.Model):
    _name = 'charge.type.currency.rate'
    _description = "Charge Type Currency Rate"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    charge_id = fields.Many2one('product.charges', string="Charge")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")

    # @api.depends('transport_type')
    # def _compute_pol_domain(self):
    #     for record in self:
    #         if record.purchase_id.transport_type_id.name == 'Air':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_11').id])]

    #         elif record.purchase_id.transport_type_id.id in 'Air':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_12').id])]

    #         elif record.transport_type.name == 'In-land':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_5').id])]

    #         else:
    #             record.dyn_filter_par = [('id', 'in', [])]