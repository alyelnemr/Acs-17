from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_available_prices = fields.One2many(comodel_name='crm.available.prices', inverse_name='crm_lead_id',
                                           string="Available Prices")
    show_request_price = fields.Boolean(string="Show Request Price", default=True)
    show_send_email = fields.Boolean(string="Show Send Email", default=False)
    show_back_to_pricing = fields.Boolean(string="Show Back To Pricing", compute='_get_back_to_pricing', default=False)
    show_available_prices = fields.Boolean(string="Show Available Price", default=False)
    count_rfqs = fields.Integer(string="Purchase", compute='get_purchase_count')

    @api.depends('stage_id')
    def _get_back_to_pricing(self):
        self.show_back_to_pricing = self.stage_id.is_follow_up_stage or self.stage_id.is_won

    def action_set_to_pricing(self):
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        self.stage_id = pricing_stage.id
        self.show_available_prices = False
        self.show_request_price = True
        self.show_send_email = False

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        self.show_back_to_pricing = True
        if self.stage_id.is_won:
            self.show_request_price = False
            self.show_send_email = False
        elif self.stage_id.is_pricing_stage:
            self.show_request_price = False
            self.show_send_email = True
            self.show_back_to_pricing = False

    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)
        self.show_available_prices = False
        self.show_request_price = False
        self.show_send_email = False
        self.show_back_to_pricing = True
        return res

    def toggle_active(self):
        res = super(CrmLead, self).toggle_active()
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
        self.show_available_prices = False
        self.show_request_price = False
        self.show_send_email = False
        self.show_back_to_pricing = False

        if self.stage_id == pricing_stage:
            self.show_request_price = True
        if self.stage_id == followup_stage:
            self.show_back_to_pricing = True
            self.show_send_email = True
        return res

    def action_view_rfqs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('crm_lead_id', '=', self.id)],
            'multi': False,
            'name': 'Purchase',
            'target': 'current',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
        }

    def get_purchase_count(self):
        for rec in self:
            count = self.env['purchase.order'].sudo().search_count([('crm_lead_id', '=', self.id)])
            rec.count_rfqs = count

    def action_request_price(self):
        if not self.pol_id:
            raise UserError(_("Please select a POL before sending the request to the pricing team."))
        if not self.pod_id:
            raise UserError(_("Please select a POD before sending the request to the pricing team."))
        if not self.transport_type_id:
            raise UserError(_("Please select a Transport Type before sending the request to the pricing team."))
        if not self.shipment_scope_id and self.transport_type_id.id != 1:
            raise UserError(_("Please select a Shipment Scope before sending the request to the pricing team."))

        domain = [('transport_type_id', '=', self.transport_type_id.id),
                  ('pol_id_country_id', '=', self.pol_id_country_id.id),
                  ('pod_id_country_id', '=', self.pod_id_country_id.id),
                  ('expiration_date', '>', fields.Date.today())]

        # If transport_type_id is not 1, add the shipment_scope_id filter
        if self.transport_type_id.id != 1:
            domain.append(('shipment_scope_id', '=', self.shipment_scope_id.id))

        available_prices = self.env['product.template'].search(domain)

        if available_prices:
            self.show_available_prices = True
            self.show_back_to_pricing = True
            self.show_request_price = False
            followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
            if not followup_stage:
                raise UserError("No Follow up stage found in the system. Please create one.")
            self.stage_id = followup_stage.id
            self.show_send_email = True
            self.crm_available_prices = [
                (5, 0, 0),  # Removes all existing records
                *[(0, 0, {'product_id': price.id}) for price in available_prices]  # Insert new records
            ]

        else:
            raise UserError(_("No available prices found for the selected criteria."))

    def action_create_rfq(self):
        return {
            'name': _('Please Assign Vendor/s For This Request Price'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'request.price.vendor',
            'view_id': self.env.ref(
                'eit_freight_pricing.view_requset_price_vendor').id,
            'context': {
                'default_crm_lead_id': self.id,
            },
            'target': 'new',
        }

    def get_lead_url(self):
        """Generates the full URL for the CRM lead form view."""
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        action_id = self.env.ref('eit_freight_workflow.crm_lead_action_pricing').id  # Adjust action ID as necessary

        return f"{base_url}/web#id={self.id}&model=crm.lead&view_type=form&action={action_id}"

    def action_send_pricing_email(self):
        # Find all users in the "eit_freight_pricing.group_pricing_user" group
        pricing_group = self.env.ref('eit_freight_pricing.group_prcing_user')
        pricing_users = self.env['res.users'].search([('groups_id', 'in', pricing_group.id)])

        # Prepare a list of email addresses
        email_list = pricing_users.mapped('partner_id.email')

        if not email_list:
            raise UserError("There are no users in the 'Pricing User' group with email addresses.")

        # Create an email template (can also use a predefined template)
        mail_template = self.env.ref('eit_freight_workflow.mail_template_lead_pricing_email')

        # Send the email to the users in the group
        if mail_template:

            action = self.env.ref('crm.crm_lead_action_pipeline').id  # Use your specific action here
            base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            lead_url = f"{base_url}/web#id={self.id}&model=crm.lead&view_type=form&action={action}"

            email_values = {
                'email_cc': False,
            }
            for email in email_list:
                email_values['email_to'] = email
                mail_template.sudo().send_mail(self.id, force_send=True, email_values=email_values)
            self.show_send_email = False

        return True
