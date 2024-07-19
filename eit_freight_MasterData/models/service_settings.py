# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api


class ServiceScope(models.Model):
    _name = "service.scope"
    _description = 'Service Scope Data'
    _order = 'code asc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    description = fields.Text(string="Refrigerated")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active')
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class ClearenceType(models.Model):
    _name = "clearence.type"
    _description = 'Clearance Type Data'
    _order = 'id asc, name asc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active')
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class TrackingStage(models.Model):
    _name = "tracking.stage"
    _description = 'Tracking Stage Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Status', default=True)
    docs_type = fields.Selection([('custom_doc', 'Customer Docs'), ('operation_doc', 'Operation Docs')])
    stage_clearence = fields.Boolean(string='Clearance')
    stage_frieght = fields.Boolean(string='Freight')

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class ActivityType(models.Model):
    _name = "activity.type"
    _description = 'Activity Type Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()
