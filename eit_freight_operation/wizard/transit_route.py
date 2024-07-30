# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class TransitRoute(models.Model):
    _name = "transit.route"

    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    port_id = fields.Many2one('port.cites', string="Origin Port", domain="[('type_id', '=', transport_type_id)]")
    port_id_origin = fields.Many2one('port.cites', string="Transit Port",
                                     domain="[('type_id', '=', transport_type_id)]")
    loaded = fields.Boolean(string="Loaded")
    expected_date = fields.Date(string="ETA")
    routing_types = fields.Selection(
        [('origin_route', 'Origin Route'), ('transist_route', 'Transit Route'), ('dest_route', 'Destination Route')],
        string="Route")
    date_start = fields.Date()
    date = fields.Date()
    actual_date = fields.Date(string="ATA")
    actual_date_start = fields.Date(string="Add ATD")
    origin_services_ids = fields.One2many('origin.services', 'trasit_route_id', string="Services")
    task_id = fields.Many2one('project.task', string="Task")
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterm")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Information")

    @api.onchange('origin_services_ids')
    def onchange_origin_services_ids(self):
        for rec in self.origin_services_ids:
            rec.task_id = self.task_id.id
            rec.routing_types = self.routing_types
            rec.shipment_scope_id = self.shipment_scope_id.id

    def create_trasit_route(self):
        for record in self:
            record.task_id.transit_route = [(4, record.id)]
