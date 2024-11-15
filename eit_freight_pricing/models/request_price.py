from odoo import models, fields, api, _
from odoo.exceptions import UserError
import json
from odoo import api, fields, models, tools, SUPERUSER_ID


class RequestPrice(models.Model):
    _name = 'request.price'
    _order = 'id desc'
    _inherit = ['mail.thread.cc',
                'mail.thread.blacklist',
                'mail.activity.mixin',
                'format.address.mixin',
                'mail.tracking.duration.mixin',
                ]
    _primary_email = 'email_from'
    _check_company_auto = True
    _track_duration_field = 'stage_id'

    name = fields.Char(string="Name", readonly=True,
                       copy=False)
    transport_type_id = fields.Many2one('transport.type', string="Transport type")
    package_ids = fields.One2many('air.package.type', 'request_price_id')
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope",
                                        domain=[('type', '=', 'sea')], )
    shipment_scope_id_in = fields.Many2one('shipment.scop', string="Shipment Scope",
                                           domain=[('type', '=', 'inland')], )
    lcl_container_type_ids = fields.One2many('lcl.container.type', 'lcl_request_price_id',
                                             string="Lcl Container Types")
    ltl_container_type_ids = fields.One2many('ltl.container.type', 'ltl_request_price_id',
                                             string="Lcl Container Types")
    fcl_container_type_ids = fields.One2many('fcl.container.type', 'request_price_id',
                                             string="Fcl Container Types")
    ftl_container_type_ids = fields.One2many('ftl.container.type', 'request_price_id_ftl',
                                             string="Ftl Container Types")

    pol = fields.Many2one('port.cites', string='POL')
    pod = fields.Many2one('port.cites', string='POD')

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    commodity_id = fields.Many2one('commodity.data', string="Commodity")
    commodity_equip = fields.Selection([
        ('dry', 'Dry'),
        ('reefer', 'Reefer'),
        ('imo', 'IMO')
    ], string="Commodity Equip")
    temperature = fields.Integer(string="Temperature")
    un_number = fields.Integer(string="UN Number")
    attachment = fields.Binary(string="Attachment", attachment=True, help="Upload your MSDS")
    incoterms_id = fields.Many2one('account.incoterms', string="Incoterms")

    cargo_readiness_date = fields.Date(string="Cargo Readiness Date")
    transit_time_duration = fields.Integer(string="Transit Time Duration")
    free_time_duration = fields.Integer(string="Free Time Duration")
    target_rate = fields.Monetary(string="Target Rate")
    currency_id = fields.Many2one('res.currency', string="Currency")
    preferred_line_id = fields.Many2one('res.partner', string="Preferred Line",
                                        domain="[('partner_type_id.name', '=', 'Shipping Line'), ('is_company', '=', True)]")
    service_needed_ids = fields.Many2many('service.scope', string="Service Needed")

    requester_notes = fields.Text(string="Requester Notes")
    date = fields.Date(string="Date")
    reporter = fields.Many2one('res.partner', string="Requester")

    # stage_id = fields.Many2one('stage.pricing')
    stage_id = fields.Many2one(
        'stage.pricing', string='Stage', index=True, tracking=True,
        compute='_compute_stage_id', readonly=False, store=True,
        default=lambda self: self.env.ref('eit_freight_pricing.stage_pricing_5').id,
        copy=False, group_expand='_read_group_stage_ids', ondelete='restrict')

    email_from = fields.Char(
        'Email', tracking=40, index='trigram',
        compute='_compute_email_from', inverse='_inverse_email_from', readonly=False, store=True)

    def action_create_rfq(self):
        return {
            'name': _('Please Assign Vendor/s For This Request Price'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.price.vendor',
            'view_id': self.env.ref(
                'eit_freight_pricing.view_requset_price_vendor').id,
            'context': {
                'default_price_id': self.id,
            },
            'target': 'new',
        }

    def _compute_stage_id(self):
        for lead in self:
            lead.stage_id = lead._stage_find(domain=[('folded', '=', False)]).id

    def _stage_find(self, domain=None, order='sequence, id', limit=1):
        search_domain = list(domain)
        return self.env['crm.stage'].search(search_domain, order=order, limit=limit)

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = []
        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    @api.depends('reporter.email')
    def _compute_email_from(self):
        for lead in self:
            if lead.reporter.email and lead._get_partner_email_update():
                lead.reporter = lead.reporter.email

    def _inverse_email_from(self):
        for lead in self:
            if lead._get_partner_email_update():
                lead.reporter.email = lead.email_from

    def _get_partner_email_update(self):
        """Calculate if we should write the email on the related partner. When
        the email of the lead / partner is an empty string, we force it to False
        to not propagate a False on an empty string.

        Done in a separate method so it can be used in both ribbon and inverse
        and compute of email update methods.
        """
        self.ensure_one()
        if self.reporter and self.email_from != self.reporter.email:
            lead_email_normalized = tools.email_normalize(self.email_from) or self.email_from or False
            partner_email_normalized = tools.email_normalize(self.reporter.email) or self.reporter.email or False
            return lead_email_normalized != partner_email_normalized
        return False

    @api.depends('transport_type_id')
    def _compute_product_id_domain(self):
        for rec in self:
            if rec.transport_type_id:
                if rec.transport_type_id.code == 'SEA':
                    rec.product_id_domain = json.dumps(
                        [('type_id', 'in', ['2'])]
                    )

                if self.transport_type_id.code == 'LND':
                    rec.product_id_domain = json.dumps(
                        [('type_id', 'in', ['3'])]
                    )
                if self.transport_type_id.code == 'AIR':
                    rec.product_id_domain = json.dumps(
                        [('type_id', 'in', ['1'])]
                    )
            else:
                rec.product_id_domain = ""

    @api.onchange('pol', 'pod')
    def onchange_pod(self):
        if self.pod and self.pol:
            if self.pod.id == self.pol.id:
                raise UserError(_('Please select another port.'
                                  'You cant choose the same port at two different locations.'))

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('request.price')
        result = super(RequestPrice, self).create(vals)
        return result


class PricePackageType(models.Model):
    _name = 'air.package.type'

    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True,
        onchange=True
    )

    qty = fields.Float(string="QTY", )
    gw_kg = fields.Float(string="GW (KG)")
    length_cm = fields.Float(string="L (CM)")
    width_cm = fields.Float(string="W (CM)")
    height_cm = fields.Float(string="H (CM)")
    cbm = fields.Float(string="CBM", compute='_compute_cbm')
    vm = fields.Float(string="VM", compute='_compute_vm')
    chw = fields.Float(string="CHW", compute="compute_chw")
    request_price_id = fields.Many2one('request.price')


    @api.depends('cbm', 'vm')
    def compute_chw(self):
        for rec in self:
            if rec.cbm >= rec.vm:
                rec.chw = rec.cbm
            else:
                rec.chw = rec.vm

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for rec in self:
            rec.cbm = (rec.length_cm * rec.width_cm * rec.height_cm)

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_vm(self):
        for rec in self:
            rec.vm = (rec.length_cm * rec.width_cm * rec.height_cm) / 6000


class FclContainerType(models.Model):
    _name = 'fcl.container.type'

    container_id = fields.Many2one('container.type', string="Container Types")
    qty = fields.Integer(string="QTY")
    gw_kg = fields.Integer(string="GW (KG)")
    request_price_id = fields.Many2one('request.price')


class FtlContainerType(models.Model):
    _name = 'ftl.container.type'

    container_id = fields.Many2one('container.type', string="Container Types")
    qty = fields.Integer(string="QTY")
    gw_kg = fields.Integer(string="GW (KG)")
    request_price_id_ftl = fields.Many2one('request.price')


class LclContainerType(models.Model):
    _name = 'lcl.container.type'

    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True,
        onchange=True
    )

    qty = fields.Float(string="QTY")
    gw_kg = fields.Float(string="GW (KG)", )
    length_cm = fields.Float(string="L (CM)")
    width_cm = fields.Float(string="W (CM)")
    height_cm = fields.Float(string="H (CM)")
    cbm = fields.Float(string="CBM", compute='_compute_cbm')
    lcl_request_price_id = fields.Many2one('request.price')

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for rec in self:
            rec.cbm = (rec.length_cm * rec.width_cm * rec.height_cm)


class LtlContainerType(models.Model):
    _name = 'ltl.container.type'

    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True,
        onchange=True
    )

    qty = fields.Float(string="QTY")
    gw_kg = fields.Float(string="GW (KG)", )
    length_cm = fields.Float(string="L (CM)")
    width_cm = fields.Float(string="W (CM)")
    height_cm = fields.Float(string="H (CM)")
    cbm = fields.Float(string="CBM", compute='_compute_cbm')
    ltl_request_price_id = fields.Many2one('request.price')

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for rec in self:
            rec.cbm = (rec.length_cm * rec.width_cm * rec.height_cm)
