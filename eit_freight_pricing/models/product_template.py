from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char(required=False)
    p_user_ids = fields.Many2many(
        'res.users',
        string="Executors",
        default=lambda self: self.env.user.ids,
        domain=[('share', '=', False)]
    )
    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    service_scope = fields.Many2one('service.scope', string="Service Scope")
    scope_ids = fields.Many2many('service.scope', string="Services")
    expiration_date = fields.Date(string='Expiration Date')
    partner_id = fields.Many2one('res.partner', string="Vendor",
                                 domain="[('partner_type_id', 'in', [4, 5, 7, 11, 12]),('is_company', '=', True)]")
    currency_id = fields.Many2one('res.currency', string="Currency", index=True)
    currency_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    package_type = fields.Many2one('package.type', string="Package Type")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope",
                                        domain=[('type', '=', 'sea')])
    container_type = fields.Many2one('container.type', string="Container Type")
    package_type_1 = fields.Many2one('package.type', string="Package Type")
    pol_id = fields.Many2one(comodel_name='port.cites', string='POL')
    pod_id = fields.Many2one(comodel_name='port.cites', string='POD')
    commodity_id = fields.Many2one('commodity.data', string="Commodity")
    transit_time_duration = fields.Integer(string="Transit Time", store=True)
    free_time_duration = fields.Integer(string="Free Time", store=True)
    shipping_line = fields.Many2one(comodel_name="res.partner", string="Shipping Line",
                                    domain="[('partner_type_id.name', '=', 'Shipping Line'), ('is_company', '=', True)]")
    air_line = fields.Many2one(comodel_name="res.partner", string="Air Line",
                               domain="[('partner_type_id.name', '=', 'Air Line'), ('is_company', '=', True)]")
    trucker = fields.Many2one(comodel_name="res.partner", string="Trucker",
                              domain="[('partner_type_id.name', '=', 'Trucker'), ('is_company', '=', True)]")
    pricing_charge_ids = fields.One2many('pricing.charges', 'product_id')
    standard_price = fields.Float(
        'Cost',
        digits='Product Price', groups="base.group_user",
        help="""Value of the product (automatically computed in AVCO).
           Used to value the product when the purchase cost is not known (e.g. inventory adjustment).
           Used to compute margins on sale orders.""")
    detailed_type = fields.Selection(
        selection_add=[('pricing', 'Pricing')],
        ondelete={'pricing': 'set default'})
    type = fields.Selection(
        selection_add=[('pricing', 'Pricing')])
    is_sale_purchase = fields.Boolean()
    is_price = fields.Boolean()
    image_id = fields.Char(string="imag")
    tot_sale = fields.One2many('total.sale.currency', 'product_sale',
                               string="Sale Per Currency")
    tot_cost = fields.One2many('total.cost.currency', 'product_cost',
                               string="Cost Per Currency")
    total_sale_in_usd = fields.Float(string="Sales Per Currency", compute="_onchange_pricing_charge_ids")
    total_cost_in_usd = fields.Float(string="Cost Per Currency", compute="_onchange_pricing_charge_ids")
    expected_revennue = fields.Float(string="Expected Revenue", compute="_onchange_pricing_charge_ids")
    conndition_ids = fields.Many2one('freight.conditions', string="Terms & Conditions")
    condition_test = fields.Text(string="Conditions")
    vessel_line_ids = fields.One2many('frieght.vessel.line', 'product_vessel_id')
    plane_line_ids = fields.One2many('frieght.plane.line', 'product_plane_id')
    is_accounting = fields.Boolean(string="Accounting", default=False)

    def _get_combination_info(
            self, combination=False, product_id=False, add_qty=1.0,
            parent_combination=False, only_template=False,
    ):
        combination_info = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty,
            parent_combination=parent_combination, only_template=only_template
        )

        combination_info['add_qty'] = 3

        return combination_info

    # dyn_filter_pro = fields.Char(string='Container/Package', compute='_compute_con_pack_domain', store=False)

    # @api.depends('container_type', 'package_type')
    # def _compute_con_pack_domain(self):
    #     for record in self:
    #         domain = []
    #         if record.container_type:
    #             domain.append(('container_type', '=', record.container_type.id))
    #         if record.package_type:
    #             domain.append(('package_type', '=', record.package_type.id))

    #         # Convert domain list to string to store in Char field
    #         record.dyn_filter_pro = str(domain)

    @api.onchange('conndition_ids')
    def _onchange_conndition_ids(self):
        if self.conndition_ids:
            self.condition_test = self.conndition_ids.Terms

    @api.depends('pricing_charge_ids')
    def _onchange_pricing_charge_ids(self):
        self.total_sale_in_usd = sum(self.pricing_charge_ids.mapped('sale_usd'))
        self.total_cost_in_usd = sum(self.pricing_charge_ids.mapped('cost_usd'))
        self.expected_revennue = self.total_sale_in_usd - self.total_cost_in_usd
        self.standard_price = self.total_cost_in_usd
        self.list_price = self.total_sale_in_usd

    @api.onchange('pricing_charge_ids')
    def compute_tot_cost(self):
        for rec in self:
            if rec.pricing_charge_ids:
                sale_list = [(5, 0, 0)]
                currency = rec.pricing_charge_ids.mapped('currency_id')
                for cur in currency:
                    amount = 0
                    for charg in rec.pricing_charge_ids:
                        if cur.id == charg.currency_id.id:
                            amount += charg.cost_price
                    val = {
                        'currency_id': cur,
                        'amount': amount
                    }
                    sale_list.append((0, 0, val))
                rec.update({'tot_cost': sale_list})
            else:
                rec.tot_cost = False

    @api.onchange('pricing_charge_ids')
    def compute_tot_sale(self):
        for rec in self:
            if rec.pricing_charge_ids:
                sale_list = [(5, 0, 0)]
                currency = rec.pricing_charge_ids.mapped('currency_id')
                for cur in currency:
                    amount = 0
                    for charg in rec.pricing_charge_ids:
                        if cur.id == charg.currency_id.id:
                            amount += charg.sale_price
                    val = {
                        'currency_id': cur,
                        'amount': amount
                    }
                    sale_list.append((0, 0, val))
                rec.update({'tot_sale': sale_list})
            else:
                rec.tot_sale = False

    @api.depends('pricing_charge_ids')
    def _compute_standard_price(self):
        for record in self:
            if record.pricing_charge_ids:
                tot_cost = tot_sale_price = 0
                for line in record.pricing_charge_ids:
                    tot_cost += line.cost_price
                    tot_sale_price += line.sale_price
                record.standard_price = tot_cost
                record.list_price = tot_sale_price
            else:
                return super(ProductTemplate, self)._compute_standard_price()

    @api.onchange('pol_id', 'pod_id')
    def onchange_pod(self):
        if self.pol_id and self.pod_id:
            if self.pol_id.id == self.pod_id.id:
                raise UserError(_('Please select another port.'
                                  'You cant choose the same port at two different locations.'))

    @api.model
    def create(self, vals):
        res = super(ProductTemplate, self).create(vals)
        transport_type = self.env['transport.type'].browse(vals.get('transport_type_id'))
        if res.detailed_type == 'pricing' and res.is_price:
            raise UserError(_('Please Insert The Price From Pricing Module'))
        if transport_type and res.detailed_type == 'pricing':
            # Update the sequence prefix dynamically based on transport_type_id
            self.env['ir.sequence'].sudo().search([('code', '=', 'product.template')]).write({
                'prefix': f'{transport_type.code}/%(y)s/'
            })

            name = self.env['ir.sequence'].next_by_code('product.template')
            res.name = name

        if res.detailed_type == 'pricing' and res.is_sale_purchase:
            raise UserError(
                _('Please add the Record from the Pricing App'))

        return res

    def write(self, vals):
        is_sale_purchase = self.env.context.get('default_is_sale_purchase', False)

        if vals.get('detailed_type') == 'pricing' and is_sale_purchase:
            raise UserError(
                _('Please add the Record from the Pricing App'))

        result = super(ProductTemplate, self).write(vals)
        for rec in self:
            if rec.p_user_ids:
                partner_ids = []
                for line in rec.p_user_ids:
                    if line.partner_id:
                        partner_ids.append(line.partner_id.id)
                rec.message_subscribe(partner_ids, None)
        return result

    @api.onchange('transport_type_id')
    def onchange_categ_ids(self):
        """Update public_categ_ids based on the transport_type selection."""
        self.ensure_one()
        if self.transport_type_id:
            # Define the mapping between transport type and public category
            category_mapping = {
                self.env.ref('eit_freight_MasterData.demo_transport_air').id: 'eit_freight_pricing.category_air',
                self.env.ref('eit_freight_MasterData.demo_transport_sea').id: 'eit_freight_pricing.category_sea',
                self.env.ref('eit_freight_MasterData.demo_transport_inland').id: 'eit_freight_pricing.category_land',
            }
            category_ref = category_mapping.get(self.transport_type_id.id)
            if category_ref:
                # Find the public category by name
                category = self.env.ref(category_ref)
                if category:
                    # Assign the category to the public_categ_ids field
                    self.public_categ_ids = [(4, category.id)]
