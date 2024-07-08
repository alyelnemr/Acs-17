# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError
from datetime import timedelta


class Task(models.Model):
    _inherit = "project.task"

    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    clearence_type_id = fields.Many2one('clearence.type', string="Direction")
    name = fields.Char(string="Opt ID", readonly=True, required=True,
                       copy=False, default='NEW')
    customer_ref = fields.Text(string="Customer Ref")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipments Scope")
    port_id = fields.Many2one('port.cites', string="POL", domain="[('type_id', '=', transport_type_id)]")
    port_id_pod = fields.Many2one('port.cites', string="POD", domain="[('type_id', '=', transport_type_id)]")
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterm")
    commidity_id = fields.Many2one('commodity.data', string="Commodity")
    commodity_equip = fields.Selection(
        string='Commodity Equip',
        selection=[('dry', 'Dry'),
                   ('imo', 'IMO'),
                   ('reefer', 'Reefer'),
                   ])
    temperature = fields.Float(string="Temperature", required=False)
    un_number = fields.Char('UN Number')
    attach_id = fields.Binary('Attachment')
    master_bl = fields.Text(string="Master B/L")
    opt_partners_lines = fields.One2many('opt.partners', 'task_id', string="Opt. Partners")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Information")
    shippinng_package_ids = fields.One2many('shipping.pacckage', 'task_id_shipping', string="Shipping Package")
    shiiping_container_ids = fields.One2many('container.data', 'task_id_container', string="Container")
    master_bl_in = fields.Text(string="Master B/L(Info)", compute="compute_master_bl")
    booking_no = fields.Text(string="Booking No")
    pol = fields.Many2one('port.cites', string="POL(Info)", compute="compute_pol")
    pod = fields.Many2one('port.cites', string="POD(Info)", compute="compute_pod")
    pickup_address = fields.Text(string="Pickup Address")
    delivery_address = fields.Text(string="Delivery Address")
    vessel_id = fields.Many2one('fright.vessels', string="Vessel")
    voyage = fields.Text(string="Voyage")
    etd = fields.Date(string="ETD")
    atd = fields.Date(string="ATD")
    eta = fields.Date(string="ETA")
    ata = fields.Date(string="ATA")
    transit_time = fields.Integer(string="Transit Time")
    shippment_order_no = fields.Text(string="Shipping Order No")
    house_bl_id = fields.One2many('house.bl', 'bl_task_id', string="House B/L ")
    routing_types = fields.Selection(
        [('origin_route', 'Origin Route'), ('transist_route', 'Transit Route'), ('dest_route', 'Destination Route')],
        string="Route")
    deatination_route = fields.Many2many('destination.route', string="Destination Route", readonly=True)
    origin_route = fields.Many2many('origin.route', string="Origin Route", readonly=True)
    transit_route = fields.Many2many('transit.route', string="Transit Route", readonly=True)
    service_ids = fields.Many2many('origin.services', compute="_compute_service_ids", readonly=False)
    dyn_filter_par = fields.Binary(string='Pol filter ', compute='_compute_pol_domain')
    sale_count = fields.Integer(string="Sale Orers", compute='get_sale_count')

    @api.depends('transport_type_id')
    def _compute_pol_domain(self):
        for record in self:
            if record.transport_type_id.name == 'Sea':
                record.dyn_filter_par = [('type', '=', 'sea')]

            elif record.transport_type_id.name == 'In-land':
                record.dyn_filter_par = [('type', '=', 'inland')]

            else:
                record.dyn_filter_par = [('id', 'in', [])]

    def create_new_coomodity(self):
        return {
            'name': _('Create New Commodity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'commodity.data',
            'view_id': self.env.ref(
                'frieght.commodity_dta_form').id,
            'target': 'new',
        }

    @api.depends('deatination_route', 'origin_route', 'transit_route')
    def _compute_service_ids(self):
        for rec in self:
            services_ids = self.env['origin.services'].search([('task_id', '=', rec.id)])
            rec.service_ids = services_ids.ids

    def origin_routing(self):
        self.routing_types = 'origin_route'
        return {
            'name': _('Origin Route'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'origin.route',
            'view_id': self.env.ref(
                'eit_freight_operation.view_origin_route').id,
            'target': 'new',
            'context': {
                'default_routing_types': self.routing_types,
                'default_transport_type_id': self.transport_type_id.id,
                'default_task_id': self.id,
                'default_incoterm_id': self.incoterm_id.id,
                'default_shipment_scope_id': self.shipment_scope_id.id
            }
        }

    def transit_routing(self):
        self.routing_types = 'transist_route'
        return {
            'name': _('Transit Route'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'transit.route',
            'view_id': self.env.ref(
                'eit_freight_operation.view_trasit_route').id,
            'target': 'new',
            'context': {
                'default_routing_types': self.routing_types,
                'default_transport_type_id': self.transport_type_id.id,
                'default_task_id': self.id,
                'default_incoterm_id': self.incoterm_id.id,
                'default_shipment_scope_id': self.shipment_scope_id.id
            }
        }

    def dest_routing(self):
        self.routing_types = 'dest_route'
        return {
            'name': _('Destination Route'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'destination.route',
            'view_id': self.env.ref(
                'eit_freight_operation.view_dest_route').id,
            'target': 'new',
            'context': {
                'default_routing_types': self.routing_types,
                'default_transport_type_id': self.transport_type_id.id,
                'default_task_id': self.id,
                'default_incoterm_id': self.incoterm_id.id,
                'default_shipment_scope_id': self.shipment_scope_id.id
            }
        }

    @api.onchange('etd', 'eta')
    def _onchange_eta(self):
        if self.eta and self.etd:
            self.transit_time = (self.eta - self.etd).days

    @api.onchange('transit_time')
    def _onchange_transit_time(self):
        if self.transit_time and self.etd:
            self.eta = self.etd + timedelta(days=self.transit_time)
            self.atd = self.eta

    def compute_pol(self):
        for rec in self:
            rec.pol = rec.port_id

    def compute_pod(self):
        for rec in self:
            rec.pod = rec.port_id_pod

    def compute_master_bl(self):
        for rec in self:
            rec.master_bl_in = rec.master_bl

    @api.onchange('port_id', 'port_id_pod')
    def onchange_port_id_pod(self):
        if self.port_id and self.port_id_pod:
            if self.port_id.id == self.port_id_pod.id:
                raise ValidationError(
                    "Please select another port."
                    "You can't choose the same port at two different locations."
                    "If you have internal transport at the same port, You can add it to the “Service” tab below after choosing the true destinations and saving")

    @api.model
    def create(self, vals):
        result = super(Task, self).create(vals)
        name = self.env['ir.sequence'].next_by_code('project.task')
        current_year = datetime.datetime.now().year
        year_str = str(current_year)[-3:].zfill(3)
        transport_code = result.transport_type_id.code if result.transport_type_id and result.transport_type_id.code else ''
        clearance_code = result.clearence_type_id.code if result.clearence_type_id and result.clearence_type_id.code else ''
        
        seequence = transport_code + "/" + clearance_code + "/" + year_str + "/"
        result.name = name.replace("X", seequence)
        return result
    
    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('project_id', '=', self.project_id.id), ('state','=', 'sale')],
            'multi': False,
            'name': 'Sale Order',
            'target': 'current',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
        }

    def get_sale_count(self):
        for rec in self:
            count = self.env['sale.order'].search_count([('project_id', '=', rec.project_id.id), ('state','=', 'sale')])
            rec.sale_count = count



class OptPartners(models.Model):
    _name = "opt.partners"

    partner_type_id = fields.Many2one('partner.type', string="Partner Type")
    partner_id = fields.Many2many('res.partner', string="Partner Name")
    task_id = fields.Many2one('project.task')
    company_id = fields.Many2one('res.company', string="Company")


class ShippingPackages(models.Model):
    _name = "shipping.pacckage"

    package_type_id = fields.Many2one('package.type', string="Package")
    quantity = fields.Integer(string="Quantity")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    height = fields.Float(string="Height")
    volume = fields.Float(string="Volume", )
    net_wight = fields.Float(string="NetWt(KG)")
    gross_weight = fields.Float(string="Gross(KG)")
    commodity_id = fields.Many2one('commodity.data', string="Commodity")
    imo = fields.Boolean(string="IMO")
    ref = fields.Boolean(string="REF")
    un_number = fields.Many2many('ir.attachment', string="UN Number")
    task_id_shipping = fields.Many2one('project.task')
    volume_wt = fields.Float(string="VOL WT")
    chw = fields.Float(string="CHW")
    temperature = fields.Integer(string="Temperature")

    @api.onchange('volume', 'width', 'height', 'length')
    def compute_volume(self):
        for rec in self:
            if rec.length and rec.width and rec.height:
                rec.volume = rec.length * rec.width * rec.height
                rec.volume_wt = (rec.length * rec.width * rec.height) / 6000
            else:
                rec.volume = 0
                rec.volume_wt = 0

    @api.onchange('gross_weight', 'volume_wt')
    def onchange_volume_wt(self):
        if self.volume_wt < self.gross_weight:
            self.chw = self.gross_weight
        else:
            self.chw = self.volume_wt


class HouseBl(models.Model):
    _name = "house.bl"

    hbl_no = fields.Char(string="HBL No")
    road_no = fields.Char(string="Road No")
    do_no = fields.Char(string="D/O No")
    war_house = fields.Char(string="Ware House")
    bl_task_id = fields.Many2one('project.task')
