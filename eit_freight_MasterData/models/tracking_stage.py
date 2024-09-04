# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api


class TrackingStage(models.Model):
    _name = "tracking.stage"
    _description = 'Tracking Stage Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Status', default=True)
    docs_type = fields.Selection([('custom_doc', 'Customer Docs'), ('operation_doc', 'Operation Docs')])
    stage_clearance = fields.Boolean(string='Clearance')
    stage_freight = fields.Boolean(string='Freight')

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()
