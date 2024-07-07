from odoo import models, fields, api, tools
from odoo.tools.translate import _
from datetime import datetime
import json
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from datetime import date


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    opportunity_source = fields.Char(string="Opportunity Source", compute="compute_opportunity_source")
    transport_type_id = fields.Many2one('transport.type', string="Transport Type", store=True)
    is_ocean_or_inland = fields.Boolean(string="Is Ocean or Inland", compute='_compute_is_ocean_or_inland',
                                        invisible=True)
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope", store=True)
    is_fcl_or_ftl = fields.Boolean(string="Is FCL or FTL", compute='_compute_is_fcl_or_ftl', invisible=True)
    is_lcl_or_ltl = fields.Boolean(string="Is LCL or LTL", compute='_compute_is_lcl_or_ltl', invisible=True)
    is_air = fields.Boolean(string="Is Air", compute='_compute_is_air', invisible=True)
    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )
    name = fields.Char(required=False, readonly=True)

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        """ Extract data from lead to create a partner.

        :param name : furtur name of the partner
        :param is_company : True if the partner is a company
        :param parent_id : id of the parent partner (False if no parent)

        :return: dictionary of values to give at res_partner.create()
        """
        email_parts = tools.email_split(self.email_from)
        res = {
            'name': partner_name,
            'user_id': self.env.context.get('default_user_id') or self.user_id.id,
            'comment': self.description,
            'team_id': self.team_id.id,
            'parent_id': parent_id,
            'phone': self.phone,
            'mobile': self.mobile,
            'email': email_parts[0] if email_parts else False,
            'title': self.title.id,
            'function': self.function,
            'street': self.street,
            'street2': self.street2,
            'zip': self.zip,
            'city': self.city,
            'country_id': self.country_id.id,
            'state_id': self.state_id.id,
            'website': self.website,
            'is_company': is_company,
            'type': 'contact',
            'partner_type_id': self.env['partner.type'].search([('code', '=', 'CST')])
        }
        if self.lang_id.active:
            res['lang'] = self.lang_id.code
        return res

    def compute_opportunity_source(self):
        for rec in self:
            if rec.type == "opportunity":
                if not rec.opportunity_source:
                    rec.opportunity_source = "OPP"
            if rec.type == "lead":
                if not rec.opportunity_source:
                    rec.opportunity_source = "Lead"

    # def redirect_lead_opportunity_view(self):
    #     self.ensure_one()
    #     action = super(CrmLead, self).redirect_lead_opportunity_view()
    #     print('actionnnn', action)
    #     action['context'].update({'default_opportunity_source': 'Lead'})
    #     print('actttt', action)
    #     return action

    @api.depends('transport_type_id')
    def _compute_product_id_domain(self):
        for rec in self:
            if rec.transport_type_id:
                if rec.transport_type_id.code == 'SEA':
                    rec.product_id_domain = json.dumps(
                        [('type', '=', 'sea')]
                    )

                if self.transport_type_id.code == 'LND':
                    rec.product_id_domain = json.dumps(
                        [('type', '=', 'inland')]
                    )
                if self.transport_type_id.code == 'AIR':
                    rec.product_id_domain = ""
            else:
                rec.product_id_domain = ""

    @api.depends('transport_type_id')
    def _compute_is_air(self):
        for record in self:
            record.is_air = record.transport_type_id.name in ['Air'] if record.transport_type_id else False

    @api.depends('transport_type_id')
    def _compute_is_ocean_or_inland(self):
        for record in self:
            record.is_ocean_or_inland = record.transport_type_id.name in ['Sea',
                                                                          'In-land'] if record.transport_type_id else False

    @api.depends('shipment_scope_id', 'is_ocean_or_inland')
    def _compute_is_fcl_or_ftl(self):
        for record in self:
            if record.shipment_scope_id and record.is_ocean_or_inland:
                record.is_fcl_or_ftl = record.shipment_scope_id.code in ['FCL', 'FTL']
            else:
                record.is_fcl_or_ftl = False

    @api.depends('shipment_scope_id', 'is_ocean_or_inland')
    def _compute_is_lcl_or_ltl(self):
        for record in self:
            if record.shipment_scope_id and record.is_ocean_or_inland:
                record.is_lcl_or_ltl = record.shipment_scope_id.code in ['LCL', 'LTL']
            else:
                record.is_lcl_or_ltl = False

    air_package_type_ids = fields.One2many(
        'crm.lead.air.package.type', 'lead_id', string="Package Types", store=True, )
    non_air_package_type_ids = fields.One2many(
        'crm.lead.non.air.package.type', 'lead_id', string="Package Types", store=True, )

    container_type_ids = fields.One2many('crm.lead.container.type', 'lead_id', string="Container Types", store=True,
                                         )

    pol_id = fields.Many2one('port.cites', string="POL", store=True)
    pod_id = fields.Many2one('port.cites', string="POD", store=True)
    commodity_id = fields.Many2one('commodity.data', string="Commodity", store=True)
    commodity_equip = fields.Selection([
        ('dry', 'Dry'),
        ('reefer', 'Reefer'),
        ('imo', 'IMO')
    ], string="Commodity Equip", store=True)

    temperature = fields.Float(string="Temperature", store=True)
    un_number = fields.Integer(string="UN Number", store=True)
    attachment = fields.Binary(string="Attachment", attachment=True, help="Upload your MSDS")
    incoterms_id = fields.Many2one('account.incoterms', string="Incoterms", store=True,
                                   )

    cargo_readiness_date = fields.Date(string="Cargo Readiness Date", store=True)
    transit_time_duration = fields.Integer(string="Transit Time", store=True)
    free_time_duration = fields.Integer(string="Free Time", store=True)
    target_rate = fields.Monetary(string="Target Rate", store=True)
    currency_id = fields.Many2one('res.currency', string="Currency", store=True,
                                  )
    preferred_line_id = fields.Many2one('res.partner', string="Preferred Line",
                                        domain="[('partner_type_id.name', '=', 'Shipping Line'), ('is_company', '=', True)]",
                                        store=True,
                                        )
    service_needed_ids = fields.Many2many('service.scope', string="Service Needed", store=True)
    opp_id = fields.Char(
        string='OPP ID', index=True, readonly=True, store=True)
    name = fields.Char(readonly=True)
    pickup_address = fields.Char(string="Pickup Address")
    pickup_address2 = fields.Text(string="Delivery Address")

    @api.onchange('pol_id', 'pod_id')
    def onchange_pod_id(self):
        if self.pol_id and self.pod_id:
            if self.pol_id.id == self.pod_id.id:
                raise UserError(
                    _("Please select another port."
                      "You can't choose the same port at two different locations."
                      "If you have internal transport at the same port, You can add it to the “Service” tab below after choosing the true destinations and saving."))

    @api.model
    def create(self, vals):
        res = super(CrmLead, self).create(vals)
        if not vals.get('name'):
            vals['name'] = self._generate_opp_id()
        vals['date_deadline'] = date.today() + timedelta(days=30)
        print(res.date_deadline)
        return super(CrmLead, self).create(vals)

    @api.model
    def _generate_opp_id(self):
        current_year = datetime.now().year
        year_suffix = str(current_year)[-2:]
        seq = self.env['ir.sequence'].next_by_code('crm.lead.opp.id') or '0000'
        return f"OPP{year_suffix}/{seq}"

    name = fields.Char(
        'Opportunity', index='trigram', required=False,
        compute='_compute_name', readonly=False, store=True)
    partner_id = fields.Many2one(domain="[('partner_type_id', 'in', [1]),('is_company', '=', True)]")

    @api.depends('partner_id')
    def _compute_name(self):
        for lead in self:
            if not lead.name and lead.partner_id and lead.partner_id.name:
                lead.name = _("%s's opportunity") % lead.partner_id.name


class Stage(models.Model):
    _inherit = "crm.stage"

    name = fields.Char(string="Pricing")
    is_pricing_stage = fields.Boolean(string="Is Pricing Stage")
    is_follow_up_stage = fields.Boolean(string="Is Follow Up Stage")

    @api.onchange('is_pricing_stage')
    def _onchhange_is_pricing_stage(self):
        if self.is_pricing_stage:
            if self.name == "Proposition":
                self.name = "Follow Up"
        else:
            if self.name == "Proposition":
                self.name = "Proposition"


class CrmLeadAirPackageType(models.Model):
    _name = 'crm.lead.air.package.type'
    _description = 'CRM Lead AIR Package Type'

    lead_id = fields.Many2one('crm.lead', string="Lead", store=True)
    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True,
        domain="[('tag_type_ids', 'in', [2])]",
        onchange=True
    )

    qty = fields.Float(string="QTY", store=True)
    gw_kg = fields.Float(string="GW (KG)", store=True)
    length_cm = fields.Float(string="L (CM)", store=True)
    width_cm = fields.Float(string="W (CM)", store=True)
    height_cm = fields.Float(string="H (CM)", store=True)
    cbm = fields.Float(string="CBM")
    vm = fields.Float(string="VM", compute='_compute_vm', store=True)
    chw = fields.Float(string="CHW", compute="compute_chw", store=True)

    def compute_chw(self):
        for rec in self:
            if rec.gw_kg * rec.qty > rec.vm:
                rec.chw = rec.gw_kg * rec.qty
            else:
                rec.chw = rec.vm

    @api.onchange('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for rec in self:
            rec.cbm = (rec.length_cm * rec.width_cm * rec.height_cm) / 1000

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_vm(self):
        for rec in self:
            rec.vm = (rec.length_cm * rec.width_cm * rec.height_cm) / 6000


class CrmLeadNonAirPackageType(models.Model):
    _name = 'crm.lead.non.air.package.type'
    _description = 'CRM Lead Non-AIR Package Type'

    lead_id = fields.Many2one('crm.lead', string="Lead", store=True)
    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True,
        domain="[('tag_type_ids', 'in', [1])]",
        onchange=True
    )
    qty = fields.Float(string="QTY", store=True)
    gw_kg = fields.Float(string="GW (KG)", store=True)
    length_cm = fields.Float(string="L (CM)", store=True)
    width_cm = fields.Float(string="W (CM)", store=True)
    height_cm = fields.Float(string="H (CM)", store=True)
    cbm = fields.Float(string="CBM")

    @api.onchange('length_cm', 'width_cm', 'height_cm')
    def _compute_cbm(self):
        for rec in self:
            rec.cbm = (rec.length_cm * rec.width_cm * rec.height_cm) / 1000


class CrmLeadContainerType(models.Model):
    _name = 'crm.lead.container.type'
    _description = 'CRM Lead Container Type'

    lead_id = fields.Many2one('crm.lead', string="Lead", store=True)
    container_type_id = fields.Many2one('container.type', string="Container Type", store=True)
    qty = fields.Float(string="QTY", store=True)
    gw_kg = fields.Float(string="GW (KG)", store=True)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_lead = fields.Boolean(default=True)

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            group_use_lead=True,
            group_proforma_sales=True
        )
        return res
