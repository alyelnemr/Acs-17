from odoo import models, fields, api, _
from odoo.exceptions import UserError

SALE_ORDER_STATE = [
    ('draft', "Quotation"),
    ('sent', "Quotation Sent"),
    ('sale', "Booking"),
    ('cancel', "Cancelled"),
]


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def default_get(self, fields):
        res = super(SaleOrder, self).default_get(fields)
        if self._context.get('default_opportunity_id'):
            crm_lead = self.env['crm.lead'].browse(self._context['default_opportunity_id'])
            res.update({
                'pol': crm_lead.pol_id.id,
                'pod': crm_lead.pod_id.id,
                'commodity': crm_lead.commodity_id.id,
                'commodity_equip': crm_lead.commodity_equip,
                'incoterms': crm_lead.incoterms_id.id,
                'shipment_scope_id': crm_lead.shipment_scope_id.id,
                'container_type': crm_lead.container_type_ids.container_type_id.id,
                'transport_type_id': crm_lead.transport_type_id.id,
            })
        return res

    transport_type_id = fields.Many2one('transport.type', string="Transport Type", store=True)
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope", store=True)
    is_ocean_or_inland = fields.Boolean(string="Is Ocean or Inland", compute='_compute_is_ocean_or_inland')
    is_fcl_or_ftl = fields.Boolean(string="Is FCL or FTL", compute='_compute_is_fcl_or_ftl')
    is_lcl_or_ltl = fields.Boolean(string="Is LCL or LTL", compute='_compute_is_lcl_or_ltl')
    container_type = fields.Many2one('container.type', string='Container Type')
    is_air = fields.Boolean(string="Is Air", compute='_compute_is_air')
    company_count = fields.Integer(default=lambda self: self.env['res.company'].search_count([]))
    rate_currency = fields.One2many('total.rate.currency', 'sale_cost',
                                    string="Rate Per Currency")
    conndition_id = fields.Many2one('freight.conditions', string="Terms & Conditions")
    vessel_line_ids = fields.One2many('sale.vessel.line', 'sale_vessel_id', string="Vessels")
    plane_line_ids = fields.One2many('sale.plane.line', 'sale_plane_id', string="Planes")
    parties_line_ids = fields.One2many('sale.parties.line', 'sale_parties_id', string="Parties")
    package_type = fields.Many2one('package.type', string='Package Type', domain="[('tag_type_ids', 'in', [1])]")
    package_types = fields.Many2one('package.type', string='Package Types', domain="[('tag_type_ids', 'in', [2])]")

    pol = fields.Many2one('port.cites', string='POL')
    pod = fields.Many2one('port.cites', string='POD')
    transit_time_duration = fields.Integer(string='Transit Time Duration')
    free_time_duration = fields.Integer(string='Free Time Duration')
    is_ocean = fields.Boolean(string="Is Ocean", compute='_compute_is_ocean')
    is_inland = fields.Boolean(string='IS Inland', compute='_compute_is_inland')
    temperature = fields.Integer(string='Temperature')
    un_number = fields.Integer(string='UN Number')
    msds_attachment = fields.Binary(string='Attachment')
    show_temperature = fields.Boolean(compute='_compute_show_temperature')
    show_un_number = fields.Boolean(compute='_compute_show_un_number')
    pickup_address = fields.Char(string="Pickup Address")
    pickup_address2 = fields.Char(string="Delivery Address")

    incoterms = fields.Many2one('account.incoterms', string='Incoterm',
                                help='International Commercial Terms are a series of predefined commercial terms used in international transactions.')
    pickup = fields.Boolean(related="incoterms.pickup")
    delivery = fields.Boolean(related="incoterms.delivery")

    charge_type = fields.Many2one('product.product', string='Charge Type')
    cost_price = fields.Float(string='Cost Price')
    currency_id = fields.Many2one('res.currency', string='Currency')
    exchange_rate = fields.Float(string='Exchange Rate', compute='_compute_exchange_rate', store=True)
    total_cost_usd = fields.Float(string='Total Cost in USD', compute='_compute_total_cost_usd', store=True)
    partner_id = fields.Many2one(domain="[('partner_type_id', 'in', [1]),('is_company', '=', True)]")
    shipment_domain = fields.Binary(string='shipment domain', compute='_compute_pol_domain')
    shipping_line = fields.Many2one('res.partner', string='Shipping Line',
                                    domain="[('partner_type_id.name', '=', 'Shipping Line'), ('is_company', '=', True)]",
                                    )
    air_line = fields.Many2one('res.partner', string='Air Line',
                               domain="[('partner_type_id.name', '=', 'Air Line'), ('is_company', '=', True)]",
                               )
    trucker = fields.Many2one('res.partner', string='Trucker',
                              domain="[('partner_type_id.name', '=', 'Trucker'), ('is_company', '=', True)]",
                              )

    commodity = fields.Many2one('commodity.data', string='Commodity')

    commodity_equip = fields.Selection([
        ('dry', 'Dry'),
        ('reefer', 'Reefer'),
        ('imo', 'IMO'),
    ], string='Commodity Equip')
    state = fields.Selection(
        selection=SALE_ORDER_STATE,
        string="Status",
        readonly=True, copy=False, index=True,
        tracking=3,
        default='draft')

    charges_ids = fields.One2many('sale.charges', 'order_id')

    @api.onchange('conndition_id')
    def _onchange_conndition_ids(self):
        if self.conndition_id:
            self.note = self.conndition_id.Terms

    @api.onchange('order_line')
    def compute_rate_currecy(self):
        for rec in self:
            if rec.order_line:
                sale_list = [(5, 0, 0)]
                currency = rec.order_line.mapped('currency_id')
                for cur in currency:
                    amount = 0
                    for charg in rec.order_line:
                        if cur.id == charg.currency_id.id:
                            amount += charg.price_total
                            print('am', amount)
                    val = {
                        'currency_id': cur,
                        'amount': amount
                    }
                    sale_list.append((0, 0, val))
                rec.update({'rate_currency': sale_list})
            else:
                rec.rate_currency = False

    @api.depends('transport_type_id')
    def _compute_is_air(self):
        for record in self:
            record.is_air = record.transport_type_id.name in ['Air'] if record.transport_type_id else False

    @api.depends('transport_type_id')
    def _compute_is_ocean_or_inland(self):
        for record in self:
            record.is_ocean_or_inland = record.transport_type_id.name in ['Sea',
                                                                          'In-land'] if record.transport_type_id else False

    @api.depends('shipment_scope_id', 'is_ocean_or_inland')
    def _compute_is_fcl_or_ftl(self):
        for record in self:
            if record.shipment_scope_id and record.is_ocean_or_inland:
                record.is_fcl_or_ftl = record.shipment_scope_id.code in ['FCL', 'FTL']
            else:
                record.is_fcl_or_ftl = False

    @api.depends('shipment_scope_id', 'is_ocean_or_inland')
    def _compute_is_lcl_or_ltl(self):
        for record in self:
            if record.shipment_scope_id and record.is_ocean_or_inland:
                record.is_lcl_or_ltl = record.shipment_scope_id.code in ['LCL', 'LTL']
            else:
                record.is_lcl_or_ltl = False

    @api.onchange('pol', 'pod')
    def onchange_pod_id(self):
        if self.pol and self.pod:
            if self.pol.id == self.pod.id:
                raise UserError(
                    _("Please select another port."
                      "You can't choose the same port at two different locations."
                      ))

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.name = vals['name'].replace('S', 'Q')
        return res

    def write(self, vals):
        if 'website_id' in vals or self.website_id:
            currency_usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
            if currency_usd_id:
                vals['currency_id'] = currency_usd_id.id
        res = super(SaleOrder, self).write(vals)
        return res

    @api.depends('transport_type_id')
    def _compute_is_ocean(self):
        for record in self:
            record.is_ocean = record.transport_type_id.name == 'Sea' if record.transport_type_id else False

    @api.depends('transport_type_id')
    def _compute_is_inland(self):
        for record in self:
            record.is_inland = record.transport_type_id.name == 'In-land' if record.transport_type_id else False

    @api.depends('commodity_equip')
    def _compute_show_temperature(self):
        for record in self:
            record.show_temperature = record.commodity_equip == 'reefer'

    @api.depends('commodity_equip')
    def _compute_show_un_number(self):
        for record in self:
            record.show_un_number = record.commodity_equip == 'imo'

    @api.depends('currency_id')
    def _compute_exchange_rate(self):
        for record in self:
            record.exchange_rate = record.currency_id.rate

    @api.depends('charge_type.lst_price', 'exchange_rate')
    def _compute_total_cost_usd(self):
        for record in self:
            record.total_cost_usd = record.charge_type.lst_price * record.exchange_rate

    @api.depends('transport_type_id')
    def _compute_pol_domain(self):
        for record in self:
            if record.transport_type_id.name == 'Sea':
                record.shipment_domain = [('type', '=', 'sea')]

            elif record.transport_type_id.name == 'In-land':
                record.shipment_domain = [('type', '=', 'inland')]

            else:
                record.shipment_domain = [('id', 'in', [])]
