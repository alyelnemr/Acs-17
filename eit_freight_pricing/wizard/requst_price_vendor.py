from odoo import api, fields, models, tools, SUPERUSER_ID


class RequestPrice(models.TransientModel):
    _name = 'request.price.vendor'

    partner_ids = fields.One2many(comodel_name='parnet.list', inverse_name='price_req_id', string="Vendor")
    crm_lead_id = fields.Many2one(comodel_name='crm.lead', string="CRM Lead")
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

    def create_rfq_from_crm(self):
        rfq_list = []

        for line in self.partner_ids:
            val = {
                'transport_type_id': self.crm_lead_id.transport_type_id.id,
                'shipment_scope_id': self.crm_lead_id.shipment_scope_id.id if self.crm_lead_id.shipment_scope_id else self.crm_lead_id.shipment_scope_id_in.id,
                'pol_id': self.crm_lead_id.pol_id.id,
                'pod_id': self.crm_lead_id.pod_id.id,
                'commodity_id': self.crm_lead_id.commodity_id.id,
                'commodity_equip': self.crm_lead_id.commodity_equip,
                'incoterms_id': self.crm_lead_id.incoterms_id.id,
                'crm_lead_id': self.crm_lead_id.id,
                'partner_id': line.partner_id.id,
                'purchase_type': 'freight'
            }
            rfq = self.env['purchase.order'].create(val)
            rfq_list.append(rfq)

        # Log a message in the CRM lead chatter
        message = 'RFQ(s) created for the following vendors: {}'.format(
            ', '.join(rfq.partner_id.name for rfq in rfq_list)
        )

        # Post the message to the chatter of the current CRM lead
        self.crm_lead_id.sudo().message_post(body=message, subject="RFQ Created")

        return {'type': 'ir.actions.act_window_close'}


class PartnerPrice(models.TransientModel):
    _name = 'parnet.list'

    partner_id = fields.Many2one('res.partner', string="Display Name",
                                 domain="[('partner_type_id', 'in', [4, 5, 7, 11, 12])]", required=True)

    phone = fields.Char(string="Phone", related="partner_id.phone")
    email = fields.Char(string="Email", related="partner_id.email")
    city = fields.Char(string="City", related="partner_id.city")
    price_req_id = fields.Many2one('request.price.vendor')
