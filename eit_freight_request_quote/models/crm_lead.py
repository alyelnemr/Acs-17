# File: your_module_name/models/crm_lead.py

from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    transport_type_id = fields.Many2one(comodel_name='transport.type', string='Transport Type')
    equipment_type_id = fields.Many2one(comodel_name='shipment.scop', string='Equipment Type')
    shipping_info_ids = fields.One2many(comodel_name='shipping.info', inverse_name='crm_lead_id', string='Shipping Info')
    additional_information = fields.Text(string='Additional Information')
    by_unit = fields.Boolean(string='By Unit')
    from_port_cities_id = fields.Many2one(comodel_name='port.cites', string='From Port Cities')
    to_port_cities_id = fields.Many2one(comodel_name='port.cites', string='To Port Cities')
    commodity_id = fields.Many2one(comodel_name='commodity.data', string='Commodity')
    cargo_readiness_date = fields.Date(string='Cargo Readiness Date')
