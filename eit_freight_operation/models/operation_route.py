# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo.exceptions import UserError
from odoo.models import NewId


class OperationRoute(models.Model):
    _name = "operation.route"
    _order = "is_main_carriage, create_date"
    _rec_name = 'routing_types'

    def default_get(self, fields_list):
        result = super(OperationRoute, self).default_get(fields_list)
        if result.get('project_task_id'):
            project_task = self.env['project.task'].browse(result['project_task_id'])
            result['clearance_type_id'] = project_task.clearence_type_id.id
            result['planned_date_start'] = project_task.planned_date_begin
            result['planned_date_end'] = project_task.date_deadline
            result['atd'] = project_task.atd
            result['ata'] = project_task.ata
        return result

    @api.depends('project_task_id')
    def get_air_line_partner_id(self):
        for rec in self:
            rec.air_line_partner_id = False
            air_line_partner_id = rec.project_task_id.opt_partners_lines.filtered(
                lambda x: x.partner_type_id.code == 'ARL')
            if air_line_partner_id:
                rec.air_line_partner_id = air_line_partner_id[0].partner_id.id if air_line_partner_id else False

    @api.depends('project_task_id')
    def get_cargo_supplier_partner_id(self):
        for rec in self:
            rec.cargo_supplier_partner_id = False
            air_line_partner_id = rec.project_task_id.opt_partners_lines.filtered(
                lambda x: x.partner_type_id.code == 'SUPL')
            if air_line_partner_id:
                rec.cargo_supplier_partner_id = air_line_partner_id[0].partner_id.id if air_line_partner_id else False

    @api.depends('project_task_id')
    def get_shipping_line_partner_id(self):
        for rec in self:
            rec.shipping_line_partner_id = False
            air_line_partner_id = rec.project_task_id.opt_partners_lines.filtered(
                lambda x: x.partner_type_id.code == 'SHL')
            if air_line_partner_id:
                rec.shipping_line_partner_id = air_line_partner_id[0].partner_id.id if air_line_partner_id else False

    @api.depends('project_task_id')
    def get_trucker_partner_id(self):
        for rec in self:
            rec.trucker_partner_id = False
            air_line_partner_id = rec.project_task_id.opt_partners_lines.filtered(
                lambda x: x.partner_type_id.code == 'TRKR')
            if air_line_partner_id:
                rec.trucker_partner_id = air_line_partner_id[0].partner_id.id if air_line_partner_id else False

    @api.depends('project_task_id')
    def get_broker_partner_id(self):
        for rec in self:
            rec.broker_partner_id = False
            air_line_partner_id = rec.project_task_id.opt_partners_lines.filtered(
                lambda x: x.partner_type_id.code == 'BRKR')
            if air_line_partner_id:
                rec.broker_partner_id = air_line_partner_id[0].partner_id.id if air_line_partner_id else False

    project_task_id = fields.Many2one(comodel_name='project.task', string="Task")
    service_scope_id = fields.Many2one(comodel_name='service.scope', string="Service")
    service_scope_id_code = fields.Char(comodel_name='service.scope', string="Service Code",
                                        related='service_scope_id.code')
    transport_type_id = fields.Many2one(comodel_name='transport.type', string="Transport Type")
    air_line_partner_id = fields.Many2one(comodel_name='res.partner', string="Airline",
                                          compute='get_air_line_partner_id', store=False)
    shipping_line_partner_id = fields.Many2one(comodel_name='res.partner', string="Shipping Line",
                                               compute='get_shipping_line_partner_id', store=False)
    trucker_partner_id = fields.Many2one(comodel_name='res.partner', string="Trucker",
                                         compute='get_trucker_partner_id', store=False)
    broker_partner_id = fields.Many2one(comodel_name='res.partner', string="Broker",
                                        compute='get_broker_partner_id', store=False)
    truck_no = fields.Char(string="Truck No", related='project_task_id.truck_no')
    truck_number = fields.Char(string="Truck Number")
    driver_name = fields.Char(string="Driver Name")
    driver_phone = fields.Char(string="Driver Phone")
    routing_types_sort = fields.Selection(selection=[('1', 'Origin Route'),
                                                     ('2', 'Transit Route'), ('3', 'Destination Route')],
                                          string="Route Type sort", default='1', compute='onchange_routing_types')
    routing_types = fields.Selection(
        selection=[('origin', 'Origin Route'), ('transit', 'Transit Route'),
                   ('destination', 'Destination Route')],
        string="Route Type", default='origin', required=True)
    port_id_from = fields.Many2one(comodel_name='port.cites', string="POL", related='project_task_id.port_id')
    port_id_to = fields.Many2one(comodel_name='port.cites', string="POD", related='project_task_id.port_id_pod')
    flight_no = fields.Char(string='Flight Number', readonly=True, related='project_task_id.flight_no')
    plane_name = fields.Char(string="Plane Name", readonly=True, related='project_task_id.plane_name')
    vessel_id = fields.Many2one(comodel_name='freight.vessels', string="Vessel", related='project_task_id.vessel_id')
    voyage_no = fields.Char(string="Voyage No", related='project_task_id.voyage_no')
    pickup_address = fields.Text(string="Pickup Address")
    delivery_address = fields.Text(string="Delivery Address")
    loaded = fields.Boolean(string="Loaded")
    planned_date_start = fields.Datetime(string="Planned Date")
    planned_date_end = fields.Datetime(string="Expected Arrival")
    transit_time = fields.Integer(string="Transit Time", related='project_task_id.transit_time')
    atd = fields.Date(string="Departure (ATD)", related='project_task_id.atd')
    ata = fields.Date(string="Arrival (ATA)", related='project_task_id.ata')
    free_time = fields.Integer(string="Free Time", related="project_task_id.free_time")
    operation_route_services_ids = fields.One2many(comodel_name='operation.route.services',
                                                   inverse_name='operation_route_id', string="Services")
    clearance_type_id = fields.Many2one(comodel_name='clearence.type', string="Direction")
    clearance_port_id = fields.Many2one(comodel_name='port.cites', string="Clearance Port")
    loading_port_id = fields.Many2one(comodel_name='port.cites', string="Loading Port")
    loading_date = fields.Date(string="Loading Date")
    terminal_warehouse_id = fields.Many2one(comodel_name='terminal.port', string="Terminal/Warehouse")
    is_main_carriage = fields.Boolean(string="Is Main Carriage")
    is_main_carriage_readonly = fields.Boolean(string="Is Main Carriage Readonly")
    routing_types_is_hidden = fields.Boolean(string="Routing Types Is Hidden",
                                             compute='_compute_routing_types_is_hidden', store=False)
    commodity_id = fields.Many2one(comodel_name='commodity.data', string="Commodity")
    commodity_id_code = fields.Char(string="HS Code")
    document_type_ids = fields.Many2many(comodel_name='document.type', string="Waiting for Documents")
    show_containers = fields.Boolean(string="Show Containers", related="project_task_id.show_containers")
    notes = fields.Text(string="Notes")
    custom_certificate_number = fields.Char(string="Custom Certificate Number")
    custom_certificate_date = fields.Date(string="Custom Certificate Date")
    procedure_end_date = fields.Date(string="Procedure End Date")
    storage_date = fields.Date(string="Storage Date")
    release_date = fields.Date(string="Release Date")
    discharge_port_id = fields.Many2one(comodel_name='port.cites', string="Discharge Port")
    discharge_date = fields.Date(string="Discharge Date")
    incoterm_id = fields.Many2one(comodel_name='account.incoterms', string="Incoterm",
                                  related='project_task_id.incoterm_id')
    document_ids = fields.One2many(comodel_name='operation.route.document', inverse_name='operation_route_id',
                                   string='Documents')
    show_free_time = fields.Boolean(string="Show Free Time", default=False)
    show_inland_for_export = fields.Boolean(string="Show Inland For Export", default=False)
    location_url = fields.Char(string="Location Url")
    contact_person_name = fields.Char(string="Contact Person Name")
    contact_person_phone = fields.Char(string="Contact Person Phone")
    destination_address = fields.Text(string="Destination Address")
    loading_address = fields.Text(string="Loading Address")
    cargo_value = fields.Float(string="Cargo Value")
    cargo_currency_id = fields.Many2one(comodel_name='res.currency', string="Cargo Currency", default=lambda self: self.env.user.company_id.currency_id)
    cargo_document_date = fields.Date(string="Cargo Document Date")
    cargo_supplier_partner_id = fields.Many2one(comodel_name='res.partner', string="Supplier",
                                                compute='get_cargo_supplier_partner_id', store=False)
    warehousing_commodity_id = fields.Many2one(comodel_name='commodity.data', string="Commodity",
                                               related='project_task_id.commodity_id')
    warehousing_commodity_equip = fields.Selection(string='Commodity Equip',
                                                   selection=[('dry', 'Dry'), ('imo', 'IMO'), ('reefer', 'Reefer'), ],
                                                   related='project_task_id.commodity_equip')
    storage_instructions = fields.Text(string="Storage Instructions")
    service_location_id = fields.Many2one(comodel_name='port.cites', string="Service Location")
    service_date = fields.Date(string="Service Date")
    service_commodity_id = fields.Many2one(comodel_name='commodity.data', string="Commodity",
                                           related='project_task_id.commodity_id')
    service_description = fields.Text(string="Service Description")

    @api.onchange('clearance_type_id')
    def onchange_clearance_type_id(self):
        self.show_inland_for_export = False
        if self.clearance_type_id.code in ('EXP', 'RXP', 'TXP'):
            self.show_inland_for_export = True

    @api.onchange('procedure_end_date')
    def onchange_procedure_end_date(self):
        if self.procedure_end_date:
            self.release_date = self.procedure_end_date

    @api.onchange('commodity_id')
    def onchange_commodity_id(self):
        if self.commodity_id:
            self.commodity_id_code = self.commodity_id.code

    @api.onchange('project_task_id')
    def onchange_project_task_id(self):
        if self.project_task_id:
            self.port_id_from = self.project_task_id.port_id.id
            self.port_id_to = self.project_task_id.port_id_pod.id
            self.clearance_type_id = self.project_task_id.clearence_type_id.id
            self.planned_date_start = self.project_task_id.planned_date_begin
            self.planned_date_end = self.project_task_id.date_deadline
            self.atd = self.project_task_id.atd
            self.ata = self.project_task_id.ata
            self.transit_time = self.project_task_id.transit_time

    @api.depends('service_scope_id')
    def _compute_routing_types_is_hidden(self):
        self.is_main_carriage = True if self.service_scope_id.service_scope_type == 'freight' else False
        self.is_main_carriage_readonly = self.service_scope_id.service_scope_type == 'freight'
        self.routing_types_is_hidden = self.service_scope_id.service_scope_type == 'freight'
        self.show_free_time = self.service_scope_id_code == 'CCL' and self.show_containers

    @api.onchange('is_main_carriage', 'service_scope_id')
    def onchange_is_main_carriage(self):
        for record in self:
            if record.is_main_carriage and not isinstance(record.id, NewId):
                # Check if another main carriage exists within the same project task
                existing_main_carriage = record.project_task_id.operation_route_ids.search(
                    [('is_main_carriage', '=', True), ('id', '!=', record.id)])
                if existing_main_carriage:
                    raise UserError(_("This Operation already have main carriage."))

    @api.depends('routing_types')
    def onchange_routing_types(self):
        for rec in self:
            rec.routing_types_sort = '1' if rec.routing_types == 'origin' else '2' if rec.routing_types == 'transit' else '3'

    @api.model_create_multi
    def create(self, vals_list):
        contain_main_carriage = False
        for vals in vals_list:
            if vals.get('commodity_id') and vals.get('commodity_id_code'):
                commodity_id = self.env['commodity.data'].browse(vals.get('commodity_id'))
                if commodity_id:
                    commodity_id.write({'code': vals.get('commodity_id_code')})
            if vals.get('is_main_carriage') and vals.get('project_task_id'):
                if contain_main_carriage:
                    raise UserError(_("This Operation already have main carriage."))
                old_main_carriage = self.env['operation.route'].search([
                    ('project_task_id', '=', vals.get('project_task_id')),
                    ('is_main_carriage', '=', True)
                ])
                contain_main_carriage = True
                if old_main_carriage:
                    raise UserError(_("This Operation already have main carriage."))
        return super(OperationRoute, self).create(vals_list)

    def write(self, vals):
        if vals.get('is_main_carriage'):
            contain_main_carriage = False
            for record in self:
                if vals.get('commodity_id_code'):
                    commodity_id = self.env['commodity.data'].browse(record.commodity_id)
                    if commodity_id:
                        commodity_id.write({'code': vals.get('commodity_id_code')})
                if vals.get('is_main_carriage'):
                    # Check if another main carriage exists within the same project task
                    if contain_main_carriage:
                        raise UserError(_("This Operation already have main carriage."))
                    existing_main_carriage = self.env['operation.route'].search([
                        ('project_task_id', '=', record.project_task_id.id),
                        ('is_main_carriage', '=', True),
                        ('id', '!=', record.id)
                    ])
                    contain_main_carriage = True
                    if existing_main_carriage:
                        raise UserError(_("This Operation already have main carriage."))

        return super(OperationRoute, self).write(vals)

    def create_operation_route(self):
        return True


class OriginServices(models.Model):
    _name = "operation.route.services"
    _rec_name = 'service_scope_id'

    service_scope_id = fields.Many2one('service.scope', string="Service")
    description = fields.Text(string="Description")
    operation_route_id = fields.Many2one('operation.route')
