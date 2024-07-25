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
    country_group_ids = fields.Many2many('res.country.group', string='Country Group',
                                         related="country_id.country_group_ids")
    display_name = fields.Char(string="Display Name", compute="compute_dispaly_name")
    type = fields.Selection([('air', 'Air'), ('sea', 'Sea'), ('island', 'Inland')], 'Is')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active', readonly=True)
    active = fields.Boolean(string='Status', default=True)
    type_id = fields.Many2many('transport.type', string="Port Is")
    country_group_id_1 = fields.Many2one('res.country.group', string='Country Group',
                                         compute="compute_country_group_id", store=True)

    @api.model
    def _default_country_group_ids(self):
        return self.env['res.country.group'].search([]).ids

    @api.depends('country_id')
    def compute_country_group_id(self):
        for rec in self:
            if rec.country_id and rec.country_id.country_group_ids:
                rec.country_group_id_1 = rec.country_id.country_group_ids[0].id
            else:
                rec.country_group_id_1 = None

    @api.depends('country_id', 'code')
    def compute_dispaly_name(self):
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
        record = super(PortCitiesTemplate, self).create(vals)
        if 'country_group_ids' in vals and record.country_id:
            current_groups = record.country_id.country_group_ids.ids
            new_groups = vals['country_group_ids'][0][2]
            if set(current_groups) != set(new_groups):
                record.country_id.write({'country_group_ids': [(6, 0, new_groups)]})
        return record

    def write(self, vals):
        result = super(PortCitiesTemplate, self).write(vals)
        if 'country_group_ids' in vals:
            for record in self:
                if record.country_id:
                    current_groups = record.country_id.country_group_ids.ids
                    new_groups = vals['country_group_ids'][0][2]
                    if set(current_groups) != set(new_groups):
                        record.country_id.write({'country_group_ids': [(6, 0, new_groups)]})
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
