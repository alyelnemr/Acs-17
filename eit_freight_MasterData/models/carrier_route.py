# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from datetime import date


class CarrierRoute(models.Model):
    _name = "carrier.route"
    _description = 'Carrier Routes'
    _order = 'create_date desc'

    name = fields.Char(string='Name', compute='_compute_name', store=False)
    pol_id = fields.Many2one('port.cites', string='POL', required=True)
    pol_country_id = fields.Many2one('res.country', string='POL Country', related='pol_id.country_id')
    pod_id = fields.Many2one('port.cites', string='POD', required=True)
    pod_country_id = fields.Many2one('res.country', string='POD Country', related='pod_id.country_id')
    route_type = fields.Selection([
        ('air', 'Air'),
        ('sea', 'Sea'),
    ], string='Route Type', required=True)
    active = fields.Boolean(string='Active', default=True)
    carrier_ids = fields.Many2many('res.partner', string='Carriers', domain=[('partner_type_id', 'in', [11, 12])])
    notes = fields.Text(string='Notes')
    equipment = fields.Selection([('dry', 'Dry'), ('reefer', 'Reefer'), ('imo', 'IMO'), ], string='Equipment')
    partner_id = fields.Many2one('res.partner', string="Partner")
    last_update = fields.Datetime(string='Last Updated On', compute='_compute_last_update', store=True)

    @api.depends('create_date', 'write_date')
    def _compute_last_update(self):
        for record in self:
            record.last_update = record.write_date if record.write_date else record.create_date

    @api.constrains('pol_id', 'pod_id')
    def _check_pol_pod_unique(self):
        for record in self:
            duplicate_routes = self.env['carrier.route'].search([('pol_id', '=', record.pol_id.id), ('pod_id', '=', record.pod_id.id), ('id', '!=', record.id)])
            if duplicate_routes:
                raise ValidationError('A route with this POL and POD already exists.')

    @api.depends('pol_id', 'pod_id', 'route_type')
    def _compute_name(self):
        for record in self:
            pol_name = record.pol_id.name if record.pol_id else ''
            pod_name = record.pod_id.name if record.pod_id else ''
            route_type_display = dict(self._fields['route_type'].selection).get(record.route_type)
            record.name = f"Route from {pol_name} to {pod_name} by {route_type_display}"
