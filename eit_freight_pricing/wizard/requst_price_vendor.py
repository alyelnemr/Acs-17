from odoo import api, fields, models, tools, SUPERUSER_ID


class RequestPrice(models.TransientModel):
    _name = 'request.price.vendor'

    partner_ids = fields.One2many('parnet.list', 'price_req_id', string="Vendor")
    price_id = fields.Many2one('request.price')

    def create_rfq(self):
        for line in self.partner_ids:
            val = {
                'transport_type_id': self.price_id.transport_type_id.id,
                'package_ids': self.price_id.package_ids[0] if self.price_id.package_ids else False,
                'shipment_scope_id': self.price_id.shipment_scope_id.id if self.price_id.shipment_scope_id else self.price_id.shipment_scope_id_in.id,
                'lcl_container_type_ids': self.price_id.lcl_container_type_ids[
                    0] if self.price_id.lcl_container_type_ids else False,
                'ltl_container_type_ids': self.price_id.ltl_container_type_ids[
                    0] if self.price_id.ltl_container_type_ids else False,
                'fcl_container_type_ids': self.price_id.fcl_container_type_ids[
                    0] if self.price_id.fcl_container_type_ids else False,
                'ftl_container_type_ids': self.price_id.ftl_container_type_ids[
                    0] if self.price_id.ftl_container_type_ids else False,
                'pol_id': self.price_id.pol.id,
                'pod_id': self.price_id.pod.id,
                'commodity_id': self.price_id.commodity_id.id,
                'commodity_equip': self.price_id.commodity_equip,
                'incoterms_id': self.price_id.incoterms_id.id,
                'price_req_id': self.price_id.id,
                'partner_id': line.partner_id.id,
                'purchase_type': 'freight'
            }
            self.env['purchase.order'].create(val)
            
        rfq_stage = self.env.ref('eit_freight_pricing.stage_pricing_6')
        if rfq_stage:
            self.price_id.stage_id = rfq_stage.id
            self.created_rfq = True


class PartnerPrice(models.TransientModel):
    _name = 'parnet.list'

    partner_id = fields.Many2one('res.partner', string="Display Name",
                                 domain="[('partner_type_id', 'in', [4, 5, 7, 11, 12])]")

    phone = fields.Char(string="Phone", related="partner_id.phone")
    email = fields.Char(string="Email", related="partner_id.email")
    city = fields.Char(string="City", related="partner_id.city")
    price_req_id = fields.Many2one('request.price.vendor')
