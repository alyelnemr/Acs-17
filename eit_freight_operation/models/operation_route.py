# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class OperationRoute(models.Model):
    _name = "operation.route"
    _order = "routing_types_sort, create_date"
    _rec_name = 'routing_types'

    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    routing_types_sort = fields.Selection(selection=[('1', 'Origin Route'), ('2', 'Transit Route'),
                                                ('3', 'Destination Route')],
                                     string="Route Type sort", default='1', compute='onchange_routing_types')
    routing_types = fields.Selection(selection=[('origin', 'Origin Route'), ('transit', 'Transit Route'),
                                                ('destination', 'Destination Route')],
                                     string="Route Type", default='origin', required=True)
    port_id_origin_from = fields.Many2one('port.cites', string="Place of Loading",
                                          domain="[('type_id.name', '=', 'In-land')]")
    port_id_origin_to = fields.Many2one('port.cites', string="Origin Port",
                                        domain="[('type_id', '=', transport_type_id)]")
    port_id_transit_from = fields.Many2one('port.cites', string="Origin Port",
                                           domain="[('type_id', '=', transport_type_id)]")
    port_id_transit_to = fields.Many2one('port.cites', string="Transit Port",
                                         domain="[('type_id', '=', transport_type_id)]")
    port_id_destination_from = fields.Many2one('port.cites', string="Transit Port",
                                               domain="[('type_id', '=', transport_type_id)]")
    port_id_destination_to = fields.Many2one('port.cites', string="Destination Port",
                                             domain="[('type_id', '=', transport_type_id)]")
    pickup_address = fields.Text(string="Pickup Address")
    delivery_address = fields.Text(string="Delivery Address")
    loaded = fields.Boolean(string="Loaded")
    planned_date_start = fields.Datetime(string="Planned Date")
    planned_date_end = fields.Datetime(string="Planned Date End")
    operation_route_services_ids = fields.One2many(comodel_name='operation.route.services',
                                                   inverse_name='operation_route_id', string="Services")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Task")

    @api.depends('routing_types')
    def onchange_routing_types(self):
        for rec in self:
            rec.routing_types_sort = '1' if rec.routing_types == 'origin' else '2' if rec.routing_types == 'transit' else '3'

    def create_operation_route(self):
        for record in self:
            record.task_id.operation_route_ids = [(4, record.id)]


class OriginServices(models.Model):
    _name = "operation.route.services"
    _rec_name = 'service_scope_id'

    service_scope_id = fields.Many2one('service.scope', string="Service")
    description = fields.Text(string="Description")
    operation_route_id = fields.Many2one('operation.route')
