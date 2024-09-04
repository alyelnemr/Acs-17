# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta


class OriginRoute(models.Model):
    _name = "origin.route"

    port_id = fields.Many2one('port.cites', string="Place of Loading", domain="[('type_id.name', '=', 'In-land')]")
    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    port_id_origin = fields.Many2one('port.cites', string="Origin Port", domain="[('type_id', '=', transport_type_id)]")
    pickup_address = fields.Text(string="Pickup Address")
    loaded = fields.Boolean(string="Loaded")
    expected_date = fields.Date(string="ETA")
    routing_types = fields.Selection(
        [('origin_route', 'Origin Route'), ('transist_route', 'Transit Route'), ('dest_route', 'Destination Route')],
        string="Route")
    date_start = fields.Date()
    date = fields.Date()
    actual_date = fields.Date(string="ATA")
    actual_date_start = fields.Date(string="Add ATD")
    origin_services_ids = fields.One2many('origin.services', 'route_id', string="Services")
    task_id = fields.Many2one('project.task', string="Task")
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterm")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Information")

    def create_origin_route(self):
        for record in self:
            record.task_id.origin_route = [(4, record.id)]

    @api.onchange('origin_services_ids')
    def onchange_origin_services_ids(self):
        for rec in self.origin_services_ids:
            rec.task_id = self.task_id.id
            rec.routing_types = self.routing_types
            rec.incoterm_id = self.incoterm_id.id
            rec.shipment_scope_id = self.shipment_scope_id.id


class OriginServices(models.Model):
    _name = "origin.services"

    service_scope_id = fields.Many2one('service.scope', string="Service")
    description = fields.Text(string="Description")
    route_id = fields.Many2one('origin.route')
    port_id = fields.Many2one('port.cites', string="Place of Loading", related="route_id.port_id")
    port_id_origin = fields.Many2one('port.cites', string="Origin Port", related="route_id.port_id_origin")
    pickup_address = fields.Text(string="Pickup Address", related="route_id.pickup_address")
    trasit_route_id = fields.Many2one('transit.route')
    dest_route_id = fields.Many2one('destination.route')
    port_id_destination = fields.Many2one('port.cites', string="Destination Port",
                                          related="dest_route_id.port_id_destination")
    pickup_address2 = fields.Text(string="Delivery Address", related="dest_route_id.pickup_address")
    task_id = fields.Many2one('project.task', string="Task")
    pol = fields.Many2one('port.cites', string="POL", related="task_id.pol")
    pod = fields.Many2one('port.cites', string="POD(", related="task_id.pod")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Information")
    routing_types = fields.Selection(
        [('origin_route', 'Origin Route'), ('transist_route', 'Transit Route'), ('dest_route', 'Destination Route')],
        string="Route")
    document_type_ids = fields.One2many('opt.documents', 'document_service_id', string="Documents")
    commodity_data_ids = fields.One2many('commodity.data.values', 'commo_data_valus', string="Commodity")
    clearence_type_id = fields.Many2one('clearence.type', string="Direction", related="task_id.clearence_type_id")
    exporter = fields.Many2many('res.partner', string="Exporter", compute="compute_exporter")
    export_customer_no = fields.Text(string="Exporter Customs No")
    customer_clerance = fields.Many2many('res.partner', string="Customs clearance Agent", compute="compute_exporter")
    customs_cert_no = fields.Text(string="Customs Certificate No")
    incoterm_id = fields.Many2one('account.incoterms', string="Incoterm")
    booking_no = fields.Text(string="Booking Number")
    certficate_date = fields.Date(string="Certificate Date")
    invoice_value = fields.Integer(string="Invoice Value")
    currency_id = fields.Many2one('res.currency', string="Currency")
    terminal = fields.Text(string="Terminal")
    stages_ids = fields.One2many('clearence.stages', 'stages_service_id', string="Clearance Stages")
    importer = fields.Many2many('res.partner', string="Importer", compute="compute_exporter")
    import_custom_no = fields.Text(string="Importer Customs No")
    b_l_number = fields.Char(string=" B/L Number")
    acid = fields.Integer(string="ACID")
    acid_date = fields.Date(string="ACID Date")
    acid_expiry = fields.Date(string="ACID Expire", compute="compute_acid_expiry")
    thc = fields.Float(string="THC")
    frieght_cost = fields.Float(string="Freight Cost")
    insurance_cost = fields.Float(string="Insurance Cost")
    import_certi_no = fields.Text(string="Import Certificate No")
    import_certi_date = fields.Text(string="Import Certificate Date")
    final_port = fields.Many2one('port.cites', string="Final Port")
    opt_payble_ids = fields.One2many('opt.payable', 'payble_route_id', string="Opt. Payable")
    opt_reciveble_ids = fields.One2many('opt.recieveble', 'reciveble_route_id', string="Opt. Receivable")
    curency_text1 = fields.Html(string="Curency Text", compute="Compute_currency_text")
    curency_textsale = fields.Html(string="Curency Text", compute="Compute_curency_textsale")
    customer = fields.Many2many('res.partner', string="Customer", compute="compute_exporter")
    vendor = fields.Many2many('res.partner', string="Vendor", compute="compute_exporter")
    bill_of_leading = fields.Text(string="Bill Of Lading No")
    bill_of_leading_date = fields.Text(string="Bill Of Lading Date")
    service_stage_id = fields.One2many('frieght.serviice.stages', 'servicestage_route_id', string="Stage")

    def Compute_currency_text(self):
        for rec in self:
            if rec.opt_payble_ids:
                result = """
                                   <table border="1" width="50%">  
                                   <tr style="border:1px solid black; font-weight:bold;">
                                   <th>Currency</th>
                                   <th>Amount</th>
                                   """
                result += """ </tr>"""

                currecy = rec.opt_payble_ids.mapped('currency')
                for cur in set(currecy):
                    total = sum(rec.opt_payble_ids.filtered(lambda x: x.currency == cur).mapped('total'))
                    result += """                  
                                                       <tr>
                                                       <td>%s</td>
                                                       <td style="text-align:right;">%.2f</td>
                                                   """ % (cur.name, total)
                self.curency_text1 = result
            else:
                self.curency_text1 = """ """

    def Compute_curency_textsale(self):
        for rec in self:
            if rec.opt_reciveble_ids:
                result = """
                                   <table border="1" width="50%">  
                                   <tr style="border:1px solid black; font-weight:bold;">
                                   <th>Currency</th>
                                   <th>Amount</th>
                                   """
                result += """ </tr>"""

                currecy = rec.opt_reciveble_ids.mapped('currency')
                for cur in set(currecy):
                    total = sum(rec.opt_reciveble_ids.filtered(lambda x: x.currency == cur).mapped('total'))
                    result += """                  
                                                       <tr>
                                                       <td>%s</td>
                                                       <td style="text-align:right;">%.2f</td>
                                                   """ % (cur.name, total)
                self.curency_textsale = result
            else:
                self.curency_textsale = """ """

    @api.depends('acid_date')
    def compute_acid_expiry(self):
        for rec in self:
            if rec.acid_date:
                rec.acid_expiry = rec.acid_date + relativedelta(months=6)
            else:
                rec.acid_expiry = False

    def compute_exporter(self):
        for rec in self:
            partner_list = []
            cust_clear = []
            importer = []
            customer = []
            vendor = []
            for line in rec.task_id.opt_partners_lines:
                for v in line.partner_id:
                    vendor.append(v.id)
                if line.partner_type_id.code == "SHP":
                    for p in line.partner_id:
                        partner_list.append(p.id)
                if line.partner_type_id.code == "CCA":
                    for c in line.partner_id:
                        cust_clear.append(c.id)
                if line.partner_type_id.code == "CNEE":
                    for cn in line.partner_id:
                        importer.append(cn.id)
                if line.partner_type_id.code == "CST":
                    for c in line.partner_id:
                        customer.append(c.id)
            rec.customer_clerance = cust_clear
            rec.exporter = partner_list
            rec.importer = importer
            rec.customer = customer
            rec.vendor = vendor

    def create_new_commodity(self):
        return {
            'name': _('Create New Commodity'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'commodity.data',
            'view_id': self.env.ref(
                'frieght.commodity_dta_form').id,
            'target': 'new',
        }
