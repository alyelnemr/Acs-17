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
    price_req_id = fields.Many2one('request.price', string="Request Price")
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    count_price_req = fields.Integer(string="Price Req Count", compute='get_request_price_count')
    scope_ids = fields.Many2many('service.scope', string="Services")
    rate_per_currency_ids = fields.One2many(
        comodel_name='charge.type.currency.rate',
        inverse_name='purchase_id',
        string="Rate Per Currency",
        store=True
    )
    charge_amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True,
                                            compute='_compute_untaxed_amount', tracking=True)

    fixed_charge_tax_details = fields.Text(
        string="Fixed Charge Tax Details",
        compute='_compute_fixed_charge_tax_details',
        readonly=True
    )

    # fixed_charge_tax_names = fields.Text(string='Tax Names', compute='_compute_fixed_charge_tax_details',)
    # fixed_charge_tax_amounts = fields.Text(string='Tax Amounts', compute='_compute_fixed_charge_tax_details',)

    total_cost_in_usd = fields.Float(string="Total Amount (USD", compute="_onchange_pricing_charge_ids")
    vat_total = fields.Monetary(
        string='Total VAT',
        compute='_compute_vat_total',
        currency_field='currency_id',
        store=True
    )
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

    withholding_tax_total = fields.Monetary(
        string='Withholding Tax',
        compute='_compute_vat_total',
        currency_field='currency_id',
        store=True
    )

    tot_amount_usd_display = fields.Char(
        string='Total Amount (USD) Display',
        compute='_compute_total_amount_usd_display',
        store=True,
        readonly=True,
    )

    @api.depends('fixed_charges_ids.tax_id', 'fixed_charges_ids.tot_cost')
    def _compute_vat_total(self):
        for order in self:
            vat_total = 0.0
            withholding_tax_total = 0.0
            for charge in order.fixed_charges_ids:
                # Calculate the VAT based on the total cost and positive tax rate
                for tax in charge.tax_id:
                    if tax.amount > 0:  # Only consider positive tax rates
                        vat_amount = charge.tot_cost * tax.amount / 100
                        vat_total += vat_amount
                    elif tax.amount < 0:  # Negative tax rates (Withholding Tax)
                        withholding_tax_total = charge.tot_cost * tax.amount / 100
                        withholding_tax_total += withholding_tax_total  # Keep as negative

            order.vat_total = vat_total
            order.withholding_tax_total = withholding_tax_total

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

    # custom_tax_summary = fields.Char(string="Custom Tax Summary", compute='_compute_custom_tax_summary', store=True)

    # @api.depends('fixed_charges_ids')
    # def _compute_custom_tax_summary(self):
    #     for order in self:
    #         taxes = order.fixed_charges_ids.mapped('tax_id')
    #         tax_summary = ''
    #         for tax in taxes:
    #             currency_symbol = order.currency_id.symbol
    #             tax_amount = sum(line.tot_cost * tax.amount / 100 for line in order.fixed_charges_ids if tax in line.tax_id)
    #             tax_summary += f"{tax.name}: {tax_amount:.2f} {currency_symbol}\n"
    #         order.custom_tax_summary = tax_summary

    @api.onchange('fixed_charges_ids')
    def _onchange_fixed_charges_ids(self):
        # Force recompute if fixed charges are changed
        self._compute_subtotal_w_o_whtax()

    # @api.depends('fixed_charges_ids')
    # def _compute_fixed_charge_tax_details(self):
    #     for order in self:
    #         tax_details = []
    #         for line in order.fixed_charges_ids:
    #             if line.tax_id:
    #                 for tax in line.tax_id:
    #                     tax_amount = line.tot_cost * (tax.amount / 100)
    #                     currency_symbol = order.currency_id.symbol or ''
    #                     formatted_tax = f"{tax.name}: {tax_amount:.2f} {currency_symbol}"
    #                     tax_details.append(formatted_tax)
    #         order.fixed_charge_tax_details = "\n".join(tax_details) if tax_details else ""

    # @api.depends('fixed_charges_ids')
    # def _compute_fixed_charge_tax_details(self):
    #     for order in self:
    #         positive_tax_totals = {}
    #         negative_tax_totals = {}
    #         max_tax_name_length = 0

    #         # Sum up tax amounts for each tax name and determine the maximum length of tax names
    #         for line in order.fixed_charges_ids:
    #             if line.tax_id:
    #                 for tax in line.tax_id:
    #                     tax_amount = line.tot_cost * (tax.amount / 100)

    #                     if tax.name not in positive_tax_totals:
    #                         positive_tax_totals[tax.name] = 0.0
    #                         negative_tax_totals[tax.name] = 0.0
    #                         max_tax_name_length = max(max_tax_name_length, len(tax.name))

    #                     if tax_amount >= 0:
    #                         positive_tax_totals[tax.name] += tax_amount
    #                     else:
    #                         negative_tax_totals[tax.name] += tax_amount

    #         tax_details = []

    #         # Format positive tax totals
    #         for tax_name, tax_amount in positive_tax_totals.items():
    #             if tax_amount > 0:
    #                 currency_symbol = order.currency_id.symbol or ''
    #                 formatted_tax = f"{tax_name:<{max_tax_name_length}}: {tax_amount:>10.2f} {currency_symbol}"
    #                 tax_details.append(f"{formatted_tax}")

    #         # Format negative tax totals
    #         for tax_name, tax_amount in negative_tax_totals.items():
    #             if tax_amount < 0:
    #                 currency_symbol = order.currency_id.symbol or ''
    #                 formatted_tax = f"{tax_name:<{max_tax_name_length}}: {tax_amount:>10.2f} {currency_symbol}"
    #                 tax_details.append(f"{formatted_tax}")

    #         # Combine all the tax details into a single string
    #         order.fixed_charge_tax_details = "\n".join(tax_details) if tax_details else ""

    @api.model
    def create(self, vals):
        # Create the purchase order first
        order = super(PurchaseOrder, self).create(vals)

        if 'fixed_charges_ids' in vals:
            for charge in order.fixed_charges_ids:
                if charge.product_id:
                    self.order_line += self.env['purchase.order.line'].create({
                        'order_id': order.id,
                        'product_id': charge.product_id.product_variant_id.id,
                        'name': charge.product_id.product_variant_id.display_name,
                        'taxes_id': [(6, 0, charge.tax_id.ids)],
                        'price_unit': charge.cost_price * charge.ex_rate,
                        'product_qty': charge.qty,  # Set quantity as needed
                    })
            order.compute_tot_cost()

            # Now that we have an order ID, create the order lines based on fixed charges
            # if 'fixed_charges_ids' in vals:
            #     # raise UserError('Test')
            #     self.compute_tot_cost()

        return order

    def write(self, vals):
        result = super(PurchaseOrder, self).write(vals)

        for charge in self.fixed_charges_ids:
            if charge.product_id:
                # Find the corresponding order line based on the product
                existing_order_line = self.order_line.filtered(
                    lambda l: l.product_id == charge.product_id.product_variant_id)

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

        if 'fixed_charges_ids' in vals:
            self.compute_tot_cost()

        return result

    @api.depends('charge_amount_untaxed', 'vat_total', 'withholding_tax_total')
    def _compute_total_amount(self):
        for order in self:
            # Calculate Total Amount: Untaxed Amount + Positive Taxes - Withholding Tax
            order.total_amount = order.charge_amount_untaxed + order.vat_total - abs(order.withholding_tax_total)

    # @api.depends('charge_amount_untaxed', 'fixed_charges_ids')
    # def _compute_total_amount(self):
    #     for order in self:
    #         total_amount = order.charge_amount_untaxed
    #         positive_taxes = 0.0
    #         withholding_taxes = 0.0

    #         for line in order.fixed_charges_ids:
    #             if line.tax_id:
    #                 for tax in line.tax_id:
    #                     tax_amount = line.tot_cost * (tax.amount / 100)
    #                     if tax.amount > 0:
    #                         positive_taxes += tax_amount
    #                     else:
    #                         withholding_taxes += tax_amount

    #         # Calculate the total amount
    #         total_amount += positive_taxes + withholding_taxes

    #         # Ensure the total matches the "Total Tax Incl. (main curr.)" column
    #         # Assuming that you have a field for the total including tax
    #         order.total_amount = total_amount

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
                    for charge in rec.fixed_charges_ids:
                        if cur.id == charge.currency_id.id:
                            amount += charge.cost_price * charge.qty
                    val = {
                        'currency_id': cur.id,
                        'amount': amount
                    }
                    sale_list.append((0, 0, val))
                rec.rate_per_currency_ids = sale_list
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

    @api.depends('fixed_charges_ids')
    def _onchange_fixed_charges_ids(self):
        self.total_amount_usd = sum(self.fixed_charges_ids.mapped('tax_inc_usd'))

    @api.depends('total_amount_usd')
    def _compute_total_amount_usd_display(self):
        for record in self:
            # Format the amount with the currency symbol after the number
            record.tot_amount_usd_display = "{:,.2f} $".format(record.total_amount_usd)
