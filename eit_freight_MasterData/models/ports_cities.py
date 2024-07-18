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


class PortCitiesType(models.Model):
    _name = "port.type"
    _description = 'Port Type Data'

    name = fields.Char()
