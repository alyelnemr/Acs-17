# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api


class PortCitiesTemplate(models.Model):
    _name = "port.cites"
    _description = 'ports & Cities Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_names_search = ['name', 'country_id']

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one('res.country', string="Country", required=True)
    # country_group_ids = fields.Many2many('res.country.group', string='Country Group')
    display_name = fields.Char(string="Display Name", compute="compute_display_name")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active', readonly=True)
    active = fields.Boolean(string='Status', default=True)
    type_id = fields.Many2many('transport.type', string="Port Is")
    country_group_id = fields.Many2one('res.country.group', string='Country Group',
                                       compute="compute_country_group_id", store=True)
    is_city = fields.Boolean(string='Is City', default=False)
    sea_river_id = fields.Many2one(comodel_name='sea.river', string='Sea River')
    ocean_id = fields.Many2one(comodel_name='ocean.data', string='Ocean', related='sea_river_id.ocean_id')

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id and len(self.country_id.country_group_ids) > 0:
            self.country_group_id = self.country_id.country_group_ids[0].id

    @api.depends('country_id')
    def compute_country_group_id(self):
        for rec in self:
            if rec.country_id and len(rec.country_id.country_group_ids) > 0:
                rec.country_group_id = rec.country_id.country_group_ids[0].id
            else:
                rec.country_group_id = None

    @api.depends('country_id', 'name')
    def compute_display_name(self):
        for rec in self:
            if rec.name and rec.country_id:
                rec.display_name = f"{rec.name}, {rec.country_id.name}"
            else:
                rec.display_name = rec.name or ""

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()

    def create(self, vals_list):
        lnd_transport_type = self.env['transport.type'].search([('code', '=', 'LND')])

        for vals in vals_list:
            if vals.get('is_city', False):
                # Ensure that the type_id includes LND
                vals['type_id'] = [(4, lnd_transport_type.id)]
            else:
                if 'type_id' in vals:
                    # Add the selected type_ids plus LND
                    selected_type_ids = vals.get('type_id', [])
                    if isinstance(selected_type_ids, list):
                        type_ids = [op[1] for op in selected_type_ids if op[0] in [4, 6]]
                        if lnd_transport_type.id not in type_ids:
                            vals['type_id'].append((4, lnd_transport_type.id))
            vals['is_city'] = False

        # After processing all vals dictionaries, create records for all
        records = super(PortCitiesTemplate, self).create(vals_list)
        return records

    def write(self, vals):
        lnd_transport_type = self.env['transport.type'].search([('code', '=', 'LND')])

        if vals.get('is_city', False):
            # Ensure that the type_id includes LND
            if 'type_id' in vals:
                if not isinstance(vals['type_id'], list):
                    vals['type_id'] = []
                vals['type_id'].append((4, lnd_transport_type.id))
            else:
                vals['type_id'] = [(4, lnd_transport_type.id)]
        else:
            if 'type_id' in vals:
                selected_type_ids = vals.get('type_id', [])
                if isinstance(selected_type_ids, list):
                    type_ids = [op[1] for op in selected_type_ids if op[0] in [4, 6]]
                    if lnd_transport_type.id not in type_ids:
                        vals['type_id'].append((4, lnd_transport_type.id))

        # Reset is_city to False regardless of the condition
        vals['is_city'] = False

        # Call the parent class write method
        result = super(PortCitiesTemplate, self).write(vals)
        return result


class TerminalPort(models.Model):
    _name = "terminal.port"
    _description = 'Terminal Port Data'

    name = fields.Char(string="Name")
    port_city_id = fields.Many2one('port.cites', string="Port / City")
    country_id = fields.Many2one('res.country', string="Country")
    address = fields.Text(string="Address")
    warehouse = fields.Boolean(string="Warehouse")
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()

    @api.onchange('port_city_id')
    def _onchange_port_city_id(self):
        if self.port_city_id:
            self.country_id = self.port_city_id.country_id


class PortCitiesType(models.Model):
    _name = "port.type"
    _description = 'Port Type Data'

    name = fields.Char()
