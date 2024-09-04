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


class ProductCharges(models.Model):
    _name = 'pricing.charges'
    _description = "Pricing Charges"

    product_id_2 = fields.Many2one('product.template', string="Charge Type",
                                   domain="[('detailed_type', '=', 'charge_type')]")
    product_id = fields.Many2one('product.template', string="Charge Type")
    sale_price = fields.Monetary(string="Sale price")
    cost_price = fields.Monetary(string="Cost price")
    qty = fields.Float(string="QTY", default=1)
    package_type = fields.Many2one('package.type', string="Container/Package")
    container_type = fields.Many2one('container.type', string="Container/Package")
    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    sale_main_curr = fields.Float(string="Sale Main Curr", compute='_compute_tot_price')
    sale_usd = fields.Float(string="Sales(USD)",
                            compute='_compute_tot_price')
    cost_main_curr = fields.Float(string="Cost Main Curr", compute='_compute_tot_price')
    cost_usd = fields.Float(string="Cost (USD)",
                            compute='_compute_tot_price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('sale_price', 'ex_rate', 'qty', 'cost_price')
    def _compute_tot_price(self):
        for record in self:
            if record.sale_price and record.ex_rate:
                record.sale_main_curr = record.sale_price * record.ex_rate
            else:
                record.sale_main_curr = 0

            if record.ex_rate:
                currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
                inverse_company_rate = currency_id.rate_ids[0].inverse_company_rate
                # inverse_company_rate = 1.0 / record.ex_rate

                record.cost_main_curr = record.cost_price * record.ex_rate
                record.cost_usd = inverse_company_rate * record.cost_main_curr
                record.sale_usd = inverse_company_rate * record.sale_main_curr
            else:
                record.cost_main_curr = 0
                record.cost_usd = 0
                record.sale_usd = 0


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    tt_days = fields.Integer(string="T.T Days")
    service_grade = fields.Selection(
        string="Service Grade",
        selection=[('good', 'Good'),
                   ('accept', 'Acceptable'),
                   ('bad', 'Bad'),
                   ('excellent', 'Excellent')
                   ])
    status = fields.Selection(
        string="Status",
        selection=[('weekly', 'Weekly'),
                   ('monthly', 'Monthly'),
                   ('suspended', 'Suspended'),
                   ('regular', 'Regular'),
                   ('blocked', 'Blocked')
                   ])
    purchase_id = fields.Many2one('purchase.order', string="RFQ Item")
    scope_ids = fields.Many2many('service.scope', string="Services")
    pol_id = fields.Many2one(comodel_name='port.cites', string='POL')
    pod_id = fields.Many2one(comodel_name='port.cites', string='POD')
    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope",
                                        domain=[('type', '=', 'sea')])
    package_type = fields.Many2one('package.type', string="Package Type")
    container_type = fields.Many2one('container.type', string="Container Type")
    note = fields.Text('Notes')

    pol_country_name = fields.Char(string="POL Country", compute="_compute_pol_country_name", store=True)
    pod_country_name = fields.Char(string="POD Country", compute="_compute_pod_country_name", store=True)

    @api.depends('pol_id')
    def _compute_pol_country_name(self):
        for record in self:
            record.pol_country_name = record.pol_id.country_id.name if record.pol_id and record.pol_id.country_id else ''

    @api.depends('pod_id')
    def _compute_pod_country_name(self):
        for record in self:
            record.pod_country_name = record.pod_id.country_id.name if record.pod_id and record.pod_id.country_id else ''

    @api.model
    def create(self, vals):
        # Fetch the transport_type_id from product.template and autofill it in product.supplierinfo
        if 'product_tmpl_id' in vals:
            product_template = self.env['product.template'].browse(vals['product_tmpl_id'])
            vals['transport_type_id'] = product_template.transport_type_id.id
            vals['shipment_scope_id'] = product_template.shipment_scope_id.id
            vals['package_type'] = product_template.package_type.id
            vals['container_type'] = product_template.container_type.id
            vals['pol_id'] = product_template.pol_id.id
            vals['pod_id'] = product_template.pod_id.id
            vals['scope_ids'] = [(6, 0, product_template.scope_ids.ids)]
        return super(ProductSupplierInfo, self).create(vals)
    
    def write(self, vals):
        # Check if product_tmpl_id is in vals or already exists on the record
        product_template_id = vals.get('product_tmpl_id') or self.product_tmpl_id.id
        if product_template_id:
            product_template = self.env['product.template'].browse(product_template_id)
            vals['transport_type_id'] = product_template.transport_type_id.id
            vals['shipment_scope_id'] = product_template.shipment_scope_id.id
            vals['package_type'] = product_template.package_type.id
            vals['container_type'] = product_template.container_type.id
            vals['pol_id'] = product_template.pol_id.id
            vals['pod_id'] = product_template.pod_id.id
            
            # Set scope_ids if it exists in product_template
            if 'product_tmpl_id' in vals or not self.scope_ids:
                if product_template.scope_ids:
                    vals['scope_ids'] = [(6, 0, product_template.scope_ids.ids)]
                else:
                    vals['scope_ids'] = [(5,)]  # Clear the field if empty
        
        return super(ProductSupplierInfo, self).write(vals)

    # def write(self, vals):
    #     # Autofill transport_type_id in case the product template's transport type changes
    #     if 'product_tmpl_id' in vals:
    #         product_template_id = vals.get('product_tmpl_id') or self.product_tmpl_id.id
    #         if product_template_id:
    #             product_template = self.env['product.template'].browse(product_template_id)
    #             vals['transport_type_id'] = product_template_id.transport_type_id.id
    #             vals['shipment_scope_id'] = product_template_id.shipment_scope_id.id
    #             vals['package_type'] = product_template_id.package_type.id
    #             vals['container_type'] = product_template_id.container_type.id
    #             vals['pol_id'] = product_template_id.pol_id.id
    #             vals['pod_id'] = product_template_id.pod_id.id
    #             vals['scope_ids'] = [(6, 0, product_template_id.scope_ids.ids)]
    #     return super(ProductSupplierInfo, self).write(vals)

    count_rfqs = fields.Integer(string="Purchase", compute='get_purchase_count')
    count_pricing = fields.Integer(string="Pricing", compute='get_pricing_count')

    def action_view_rfqs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('id', '=', self.purchase_id.id), ('purchase_type', '=', 'freight')],
            'multi': False,
            'name': 'Purchase',
            'target': 'current',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
        }
    
    def action_view_pricing(self):
        self.ensure_one()
        tree_view_id = self.env.ref('eit_freight_pricing.product_template_tree_view_pricing2').id
        form_view_id = self.env.ref('eit_freight_pricing.product_template_form_view_pricing2').id
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('id', '=', self.product_tmpl_id.id), ('detailed_type', '=', 'pricing')],
            'multi': False,
            'name': 'Pricing',
            'target': 'current',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'views': [
            (tree_view_id, 'tree'),  # Tree view
            (form_view_id, 'form')   # Form view
        ],
            # 'view_id': self.env.ref('eit_freight_pricing.product_template_tree_view_pricing2').id,
        }

    def get_purchase_count(self):
        for rec in self:
            count = self.env['purchase.order'].search_count([('id', '=', self.purchase_id.id), ('purchase_type', '=', 'freight')])
            rec.count_rfqs = count

    def get_pricing_count(self):
        for rec in self:
            count = self.env['product.template'].search_count([('id', '=', self.product_tmpl_id.id), ('detailed_type', '=', 'pricing')])
            rec.count_pricing = count
    
    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.partner_id = rec.purchase_id.partner_id.id


class TotalSaleCurrency(models.Model):
    _name = 'total.sale.currency'
    _description = "Total sale currency"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_sale = fields.Many2one('product.template')


class TotalCostCurrency(models.Model):
    _name = 'total.cost.currency'
    _description = "Total cost currency"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_cost = fields.Many2one('product.template')


class FrieghtVessalsLine(models.Model):
    _name = 'frieght.vessel.line'

    vessel_id = fields.Many2one('freight.vessels', string="Vessel")
    voyage_number = fields.Char(string="Voyage Number")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    tt_day = fields.Integer(string="T.T Day")
    product_vessel_id = fields.Many2one('product.template')

    @api.onchange('tt_day')
    def _compute_eta(self):
        for record in self:
            if record.etd and record.tt_day:
                etd_date = fields.Date.from_string(record.etd)
                eta_date = etd_date + timedelta(days=record.tt_day)
                record.eta = fields.Date.to_string(eta_date)


    @api.onchange('eta')
    def _compute_tt_day(self):
        for record in self:
            if record.etd and record.eta:
                etd_date = fields.Date.from_string(record.etd)
                eta_date = fields.Date.from_string(record.eta)
                delta = eta_date - etd_date
                record.tt_day = delta.days


class FrieghtPlanesLine(models.Model):
    _name = 'frieght.plane.line'

    plane_id = fields.Many2one('freight.airplane', string="Plane")
    product_plane_id = fields.Many2one('product.template')
    voyage_number = fields.Char(string="Voyage Number")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    tt_day = fields.Integer(string="T.T Day")

    @api.onchange('etd', 'tt_day')
    def _compute_eta(self):
        for record in self:
            if record.etd and record.tt_day:
                record.eta = record.etd + timedelta(days=record.tt_day)
            else:
                record.eta = False

    @api.onchange('etd', 'eta')
    def _compute_tt_day(self):
        for record in self:
            if record.etd and record.eta:
                delta = record.eta - record.etd
                record.tt_day = delta.days
            else:
                record.tt_day = 0

