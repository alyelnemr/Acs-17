# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api
from odoo.exceptions import ValidationError
from datetime import date


class CommodityData(models.Model):
    _name = "commodity.data"
    _description = 'Commodity Data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Hs Code", required=True)
    tax = fields.Integer(string="Import Tax")
    vat = fields.Integer(string="Vat")
    group_id = fields.Many2one('commodity.group', string="Commodity Group")
    type = fields.Selection([('dry', 'Dry'), ('reefer', 'Reefer'), ('imo', 'IMO')], 'Commodity Equip')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status', readonly=True)
    tag_id = fields.Many2one('frieght.tags', string="Tags One")
    active1 = fields.Boolean(string='Status', default=True)
    import_approval = fields.One2many('commodity.data.approval.import', 'approval_data_id_import'
                                      , string="Import Approvals")
    export_approval = fields.One2many('commodity.data.approval.export', 'approval_data_id_export'
                                      , string="Export Approvals")
    export_custom = fields.One2many('commodity.data.custom.export', 'custom_data_id_import'
                                    , string="Export Req")
    import_custom = fields.One2many('commodity.data.custom.import', 'custom_data_id_import'
                                    , string="Import Req")
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Created by")
    created_on = fields.Date(default=date.today(), string="Created on")
    updated_by = fields.Many2one('res.users', string="Last Updated by")
    updated_on = fields.Date(string="Last Updated on")
    industry_id = fields.Many2one(
        comodel_name='res.partner.industry', string="Industry")
    req_id = fields.Many2many('commodity.req', string="Commodity Equip")
    tag_id_1 = fields.Many2many('frieght.tags', string="Tags")
    export_tax = fields.Integer(string="Export Tax")

    @api.onchange('active1')
    def _onchange_active(self):
        for rec in self:
            if not rec.active1:
                rec.toggle_active()

    @api.constrains('code')
    def _check_even_numbers(self):
        for record in self:
            if record.code:
                counts = 0
                numbers = record.code
                # if len(numbers) != 5:
                #     raise ValidationError("You must enter five numbers separated by spaces.")
                # for number in numbers:
                #     num = int(number)
                #     if num % 2 == 0:
                #         counts += 1
                if len(numbers) == 6 or len(numbers) == 8 or len(numbers) == 10:
                    print('runinh')
                else:
                    raise ValidationError("HSCode Format Can Accept 6 Or 8 Or 10 Digits")

    def write(self, values):
        if 'code' in values:
            self._check_even_numbers()
        values['updated_on'] = date.today()
        values['updated_by'] = self.env.user.id
        return super(CommodityData, self).write(values)

    @api.model
    def create(self, values):
        record = super(CommodityData, self).create(values)
        record._check_even_numbers()
        return record
