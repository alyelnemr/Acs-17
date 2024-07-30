# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class CommodityDataCustomExport(models.Model):
    _name = "commodity.data.custom.export"
    _description = 'Export Req .Needs'

    name = fields.Text(string="Description")
    custom_data_id_import = fields.Many2one('commodity.data')
