from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date


class ProductTemplate(models.Model):
    _inherit = "product.template"

    name = fields.Char(required=False)
    p_user_ids = fields.Many2many('res.users', string="Executors")
    transport_type_id = fields.Many2one('transport.type', string="Transport Type", required=True)
    service_scope = fields.Many2one('service.scope', string="Service Scope")
    expiration_date = fields.Date(string='Expiration Date')
    partner_id = fields.Many2one('res.partner', string="Vendor",
                                 domain="[('partner_type_id', 'in', [4, 5, 7, 11, 12]),('is_company', '=', True)]")
    currency_id = fields.Many2one('res.currency', string="Currency")
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
                               string="Total Currency For Sale")
    tot_cost = fields.One2many('total.cost.currency', 'product_cost',
                               string="Total Currency For Cost")
    total_sale_in_usd = fields.Float(string="Total Sales in USD")
    total_cost_in_usd = fields.Float(string="Total Cost in USD")
    expected_revennue = fields.Float(string="Expected Revenue")
    conndition_ids = fields.Many2many('freight.conditions', string="Terms & Conditions")

    @api.onchange('pricing_charge_ids')
    def _onchange_pricing_charge_ids(self):
        self.total_sale_in_usd = sum(self.pricing_charge_ids.mapped('tot_cost'))
        self.total_cost_in_usd = sum(self.pricing_charge_ids.mapped('tot_cost_uusd'))
        self.expected_revennue = self.total_sale_in_usd - self.total_cost_in_usd

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
                            amount += charg.tot_in_cost
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
                            amount += charg.tot_cost_fr
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

        return res


class ProductCharges(models.Model):
    _name = 'pricing.charges'
    _description = "Pricing Charges"

    product_id_2 = fields.Many2one('product.template', string="Charge Type",
                                   domain="[('detailed_type', '=', 'charge_type')]")
    product_id = fields.Many2one('product.template', string="Charge Type")
    sale_price = fields.Monetary(string="Sale price")
    cost_price = fields.Monetary(string="Cost price")
    qty = fields.Float(string="QTY", default=1)
    package_type = fields.Many2one('package.type', string="Package Type")
    container_type = fields.Many2one('container.type', string="Container Type")
    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    tot_cost_fr = fields.Float(string="Total sale Currency", compute='_compute_tot_price')
    tot_cost = fields.Float(string="Total Sales(USD)",
                            compute='_compute_tot_price')
    tot_in_cost = fields.Float(string="Total Cost Currency", compute='_compute_tot_price')
    tot_cost_uusd = fields.Float(string="Total Cost(USD)",
                                 compute='_compute_tot_price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('sale_price', 'ex_rate', 'qty', 'cost_price')
    def _compute_tot_price(self):
        for record in self:
            if record.sale_price and record.ex_rate:
                record.tot_cost_fr = record.sale_price * record.ex_rate
            else:
                record.tot_cost_fr = 0

            currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
            today = date.today()
            currency_rate = self.env['res.currency']._get_conversion_rate(
                from_currency=record.currency_id,
                to_currency=currency_id,
                company=record.company_id,
                date=today,
            )
            print('cureeeeee', currency_rate)
            record.tot_in_cost = record.cost_price * record.ex_rate
            record.tot_cost_uusd = currency_rate * record.tot_in_cost
            record.tot_cost = currency_rate * record.tot_cost_fr


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


class TotalSaleCurrency(models.Model):
    _name = 'total.sale.currency'

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_sale = fields.Many2one('product.template')


class TotalCostCurrency(models.Model):
    _name = 'total.cost.currency'

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_cost = fields.Many2one('product.template')
