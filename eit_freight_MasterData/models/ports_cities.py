# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api


class PortCitiesTemplate(models.Model):
    _name = "port.cites"
    _description = 'ports & Cities Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    country_id = fields.Many2one('res.country', string="Country", required=True)
    country_group_ids = fields.Many2many('res.country.group', string='Country Group')
    display_name = fields.Char(string="Display Name", compute="compute_display_name")
    type = fields.Selection([('air', 'Air'), ('sea', 'Sea'), ('island', 'Inland')], 'Is')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active', readonly=True)
    active = fields.Boolean(string='Status', default=True)
    type_id = fields.Many2many('transport.type', string="Port Is")
    country_group_id_1 = fields.Many2one('res.country.group', string='Country Group',
                                         compute="compute_country_group_id", store=True)

    @api.onchange('country_id')
    def _onchange_country_id(self):
        if self.country_id:
            self.country_group_ids = self.country_id.country_group_ids

    @api.depends('country_id')
    def compute_country_group_id(self):
        for rec in self:
            if rec.country_id and rec.country_id.country_group_ids:
                rec.country_group_id_1 = rec.country_id.country_group_ids[0].id
            else:
                rec.country_group_id_1 = None

    @api.depends('country_id', 'code')
    def compute_display_name(self):
        for rec in self:
            str = ""
            if rec.name:
                str = str + rec.name + "-"
            if rec.country_id:
                str = str + rec.country_id.name
            rec.display_name = str

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()

    def create(self, vals):
        # Create the record first
        record = super(PortCitiesTemplate, self).create(vals)

        # Update country_group_ids directly if both country_group_ids and country_id are present in vals
        if 'country_group_ids' in vals and 'country_id' in vals:
            country = self.env['res.country'].browse(vals['country_id'])
            # Flatten the list of operations to get the new groups
            new_groups = []
            for operation in vals['country_group_ids']:
                if operation[0] == 4:
                    new_groups.append(operation[1])
                elif operation[0] == 6:
                    new_groups = operation[2]
                    break
            if set(new_groups) != set(country.country_group_ids.ids):
                country.sudo().write({'country_group_ids': [(6, 0, new_groups)]})

        return record

    def write(self, vals):
        result = super(PortCitiesTemplate, self).write(vals)
        if 'country_group_ids' in vals:
            new_groups = vals['country_group_ids'][0][2]
            for record in self:
                if record.country_id and set(record.country_id.country_group_ids.ids) != set(new_groups):
                    record.country_id.update({'country_group_ids': [(6, 0, new_groups)]})
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
