# -*- coding: utf-8 -*-
from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta

CLOSED_STATES = {
    '1_done': 'Closed',
    '1_under_settlement': 'Under Settlement',
    '1_canceled': 'Canceled',
}


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
    shipping_package_ids = fields.One2many('shipping.package', 'task_id_shipping', string="Shipping Package")
    shipping_container_ids = fields.One2many('shipping.container', 'project_task_id', string="Container")
    master_bl_in = fields.Text(string="Master B/L(Info)", compute="compute_master_bl")
    booking_no = fields.Char(string="Booking No")
    pol = fields.Many2one('port.cites', string="POL(Info)", compute="compute_pol")
    pod = fields.Many2one('port.cites', string="POD(Info)", compute="compute_pod")
    pickup_address = fields.Text(string="Pickup Address")
    delivery_address = fields.Text(string="Delivery Address")
    vessel_id = fields.Many2one('freight.vessels', string="Vessel")
    voyage_no = fields.Char(string="Voyage No")
    etd = fields.Date(string="ETD")
    atd = fields.Date(string="Departure (ATD)")
    eta = fields.Date(string="ETA")
    ata = fields.Date(string="Arrival (ATA)")
    transit_time = fields.Integer(string="Transit Time")
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
    state = fields.Selection([
        ('01_in_progress', 'In Progress'),
        ('02_changes_requested', 'Planned Date Changed'),  # Updated from Changes Requested to Date Changed
        ('03_approved', 'Invoicing'),  # Updated from Approved to Arrived
        *CLOSED_STATES.items(),
        ('04_waiting_normal', 'Waiting'),
    ], string='State', copy=False, default='01_in_progress', required=True,
        readonly=False, store=True, index=True, tracking=True)
    state_selectable = fields.Selection([
        ('01_in_progress', 'In Progress'),
        ('02_changes_requested', 'Planned Date Changed'),
        ('03_approved', 'Invoicing'),
        ('1_canceled', 'Canceled'),
        ('1_done', 'Closed',)
    ], string='State', copy=False, default='01_in_progress', required=True)
    expecting_date_closing = fields.Date(string="Expecting Date Closing")
    should_set_date_closing = fields.Boolean(string="Should Set Date Closing", default=False)
    services = fields.Many2many('service.scope', string="Services")
    show_packages = fields.Boolean(string="Show Packages", default=False)
    show_containers = fields.Boolean(string="Show Containers", default=False)
    show_transportation = fields.Boolean(string="Show Transportation", default=False)
    show_transportation_inland = fields.Boolean(string="Show Transportation Inland", default=False)
    show_bill_leading_details = fields.Boolean(string="Show Bill Leading Details", default=False)
    bill_of_lading_issuance = fields.Date(string="Bill of Lading Issuance")
    terminal_port_id = fields.Many2one(comodel_name='terminal.port', string="Terminal Port",
                                       domain="[('warehouse', '=', False)]")
    bill_lading_type_id = fields.Many2one(comodel_name='bill.leading.type', string="Bill Lading Type")
    bill_lading_collection = fields.Selection([('prepaid', 'Prepaid'), ('collect', 'Collect')],
                                              default='prepaid',
                                              string="Bill Lading Collection")
    delivery_order_no = fields.Char(string="Delivery Order No")
    plane_name = fields.Char(string="Plane Name")
    flight_no = fields.Char(string="Flight No")
    truck_no = fields.Char(string="Truck No")
    acid_no = fields.Char(string="ACID No")
    acid_issuance_date = fields.Date(string="ACID Issuance Date")
    foreign_exporter_id = fields.Char(string="Foreign Exporter ID")
    foreign_exporter_country_id = fields.Many2one(comodel_name='res.country', string="Foreign Exporter Country")
    acid_expiry_date = fields.Date(string="ACID Expiry Date")
    is_house_bl = fields.Boolean(string="House B/L", default=False)
    is_consolidation = fields.Boolean(string="Consolidation", default=False)
    terminal_port_warehouse_id = fields.Many2one(comodel_name='terminal.port', string="Warehouse",
                                                 domain="[('warehouse', '=', True)]")

    @api.onchange('acid_issuance_date')
    def _onchange_acid_issuance_date(self):
        if self.acid_issuance_date:
            self.acid_expiry_date = self.acid_issuance_date + relativedelta(months=6)

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

    @api.onchange('transport_type_id', 'shipment_scope_id')
    def show_container_package(self):
        for rec in self:
            rec.show_containers = False
            rec.show_packages = False
            rec.show_transportation = False
            rec.show_transportation_inland = False
            rec.show_bill_leading_details = False
            if rec.transport_type_id.code == 'AIR':
                rec.show_packages = True
                rec.show_transportation = True
            if rec.transport_type_id.code == 'SEA':
                rec.show_bill_leading_details = True
                if rec.shipment_scope_id.code == 'LCL':
                    rec.show_packages = True
                if rec.shipment_scope_id.code == 'FCL':
                    rec.show_containers = True
            if rec.transport_type_id.code == 'LND':
                rec.show_transportation_inland = True
                if rec.shipment_scope_id.code == 'LTL':
                    rec.show_packages = True
                if rec.shipment_scope_id.code == 'FTL':
                    rec.show_containers = True

    @api.onchange('transport_type_id', 'clearence_type_id')
    def create_sequence(self):
        self.shipment_scope_id = False
        if self.transport_type_id and self.clearence_type_id:
            name = self.env['ir.sequence'].next_by_code('project.task')
            current_year = datetime.datetime.now().year
            year_str = str(current_year)[-3:].zfill(3)
            transport_code = self.transport_type_id.code if self.transport_type_id and self.transport_type_id.code else ''
            clearance_code = self.clearence_type_id.code if self.clearence_type_id and self.clearence_type_id.code else ''

            seequence = transport_code + "/" + clearance_code + "/" + year_str + "/"
            self.name = name.replace("X", seequence)

    @api.model
    def create(self, vals):
        project = self.env['project.project'].browse(vals.get('project_id'))
        if not vals.get('stage_id') and project:
            vals['stage_id'] = project.type_ids[0].id  # Set the first stage as default
        if vals.get('state') == '1_under_settlement':
            vals['stage_id'] = self.env.ref('eit_freight_operation.stage_invoice').id
        elif vals.get('state') in ['01_in_progress', '02_changes_requested']:
            vals['stage_id'] = self.env.ref('eit_freight_operation.stage_open').id
        elif vals.get('state') == '1_done':
            vals['stage_id'] = self.env.ref('eit_freight_operation.stage_closed').id
        elif vals.get('state') == '03_approved':
            vals['stage_id'] = self.env.ref('eit_freight_operation.stage_invoice').id
        elif vals.get('state') == '1_canceled':
            vals['stage_id'] = self.env.ref('eit_freight_operation.stage_canceled').id
        return super(Task, self).create(vals)

    def write(self, vals):
        # Prevent recursion by checking if the stage change is necessary
        for task in self:
            new_state = vals.get('state_selectable', False)
            is_admin = self.env.user.has_group('eit_freight_MasterData.group_freight_admin')
            if new_state:
                vals['should_set_date_closing'] = False
                if new_state != '1_done' and task.state == '1_done' and not is_admin:
                    raise UserError('Only Admin can restore task from closed state')
                if new_state != '1_done' and task.state == '1_done' and is_admin:
                    vals['should_set_date_closing'] = True
                    vals['expecting_date_closing'] = datetime.date.today() + timedelta(days=1)
                if new_state == '1_under_settlement':
                    new_stage_id = self.env.ref('eit_freight_operation.stage_invoice').id
                elif new_state in ['01_in_progress', '02_changes_requested']:
                    new_stage_id = self.env.ref('eit_freight_operation.stage_open').id
                elif new_state == '1_done' and is_admin:
                    vals['should_set_date_closing'] = False
                    vals['expecting_date_closing'] = False
                    new_stage_id = self.env.ref('eit_freight_operation.stage_closed').id
                elif new_state == '1_canceled':
                    new_stage_id = self.env.ref('eit_freight_operation.stage_canceled').id
                elif new_state == '03_approved':
                    new_stage_id = self.env.ref('eit_freight_operation.stage_invoice').id
                else:
                    new_stage_id = task.stage_id.id

                vals['stage_id'] = new_stage_id
                vals['state'] = new_state

        return super(Task, self).write(vals)

    @api.onchange('state')
    def _onchange_state_closed(self):
        for task in self:
            if task.state == '1_done':
                warning_message = {
                    'title': "Are you sure?",
                    'message': "Do you want to close operation no. = %s?\nNote that you may not have access to this operation after closing!" % (
                        task.name),
                }
                task.stage_id = self.env.ref('eit_freight_operation.stage_closed').id
                return {'warning': warning_message}

    # @api.model
    # def create(self, vals):
    #     result = super(Task, self).create(vals)
    #     name = self.env['ir.sequence'].next_by_code('project.task')
    #     current_year = datetime.datetime.now().year
    #     year_str = str(current_year)[-3:].zfill(3)
    #     transport_code = result.transport_type_id.code if result.transport_type_id and result.transport_type_id.code else ''
    #     clearance_code = result.clearence_type_id.code if result.clearence_type_id and result.clearence_type_id.code else ''

    #     seequence = transport_code + "/" + clearance_code + "/" + year_str + "/"
    #     result.name = name.replace("X", seequence)
    #     return result

    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('project_id', '=', self.project_id.id), ('state', '=', 'sale')],
            'multi': False,
            'name': 'Sale Order',
            'target': 'current',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
        }

    def get_sale_count(self):
        for rec in self:
            count = self.env['sale.order'].search_count(
                [('project_id', '=', rec.project_id.id), ('state', '=', 'sale')])
            rec.sale_count = count


class OptPartners(models.Model):
    _name = "opt.partners"
    _description = "Opt partners"

    partner_type_id = fields.Many2one('partner.type', string="Partner Type", required=True)
    partner_id = fields.Many2one('res.partner', string="Company Name",
                                 domain="[('partner_type_id', '=', partner_type_id), ('is_company', '=', True)]")
    phone = fields.Char(related='partner_id.phone', string="Phone")
    email = fields.Char(related='partner_id.email', string="Email")
    sales_person = fields.Many2one(related='partner_id.user_id', string="Salesperson")
    # activity_ids = fields.One2many(related='partner_id.activity_ids', string="Activities")
    country_id = fields.Many2one(related='partner_id.country_id', string="Country")
    task_id = fields.Many2one('project.task')
    company_id = fields.Many2one('res.company', string="Company")


class HouseBl(models.Model):
    _name = "house.bl"
    _description = "House bl"

    hbl_no = fields.Char(string="HBL No")
    road_no = fields.Char(string="Road No")
    do_no = fields.Char(string="D/O No")
    war_house = fields.Char(string="Ware House")
    bl_task_id = fields.Many2one('project.task')
