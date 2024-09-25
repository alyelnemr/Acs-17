from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    crm_available_prices = fields.One2many(comodel_name='crm.available.prices', inverse_name='crm_lead_id',
                                           string="Available Prices")
    show_request_price = fields.Boolean(string="Show Request Price", default=True)
    show_send_email = fields.Boolean(string="Show Send Email", default=False)
    is_new_stage = fields.Boolean(string="Is New Stage", compute='get_new_stage')
    is_won_stage = fields.Boolean(string="Is Won Stage", related='stage_id.is_won')
    is_followup_stage = fields.Boolean(string="Is Follow Up Stage", related='stage_id.is_follow_up_stage')
    is_pricing_stage = fields.Boolean(string="Is Pricing Stage", related='stage_id.is_pricing_stage')
    count_rfqs = fields.Integer(string="Purchase", compute='get_purchase_count')

    @api.depends('stage_id')
    def get_new_stage(self):
        self.is_new_stage = self.stage_id.name == 'New'

    def action_set_to_pricing(self):
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        self.stage_id = pricing_stage.id
        self.show_request_price = True
        self.show_send_email = False

    def action_set_to_followup(self):
        followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
        self.stage_id = followup_stage.id

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        if self.stage_id.is_won:
            self.show_request_price = False
            self.show_send_email = False
        elif self.stage_id.is_pricing_stage:
            self.show_request_price = False
            self.show_send_email = True

    def action_set_lost(self, **additional_values):
        res = super().action_set_lost(**additional_values)
        self.show_request_price = False
        self.show_send_email = False
        return res

    def toggle_active(self):
        res = super(CrmLead, self).toggle_active()
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
        self.show_request_price = False
        self.show_send_email = False

        if self.stage_id == pricing_stage:
            self.show_request_price = True
        if self.stage_id == followup_stage:
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

    def action_move_pricing(self):
        if not self.pol_id:
            raise UserError(_("Please select a POL before moving to the pricing stage."))
        if not self.pod_id:
            raise UserError(_("Please select a POD before moving to the pricing stage."))
        if not self.transport_type_id:
            raise UserError(_("Please select a Transport Type before moving to the pricing stage."))
        if not self.shipment_scope_id and self.transport_type_id.id != 1:
            raise UserError(_("Please select a Shipment Scope before moving to the pricing stage."))
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        self.stage_id = pricing_stage.id
        self.check_for_prices_update()

    def action_prices_update(self):
        return self.check_for_prices_update(show_message=True)

    def check_for_prices_update(self, show_message=False):
        if not self.pol_id:
            raise UserError(_("Please select a POL before moving to the pricing stage."))
        if not self.pod_id:
            raise UserError(_("Please select a POD before moving to the pricing stage."))
        if not self.transport_type_id:
            raise UserError(_("Please select a Transport Type before moving to the pricing stage."))
        if not self.shipment_scope_id and self.transport_type_id.id != 1:
            raise UserError(_("Please select a Shipment Scope before moving to the pricing stage."))

        domain = [('transport_type_id', '=', self.transport_type_id.id),
                  ('pol_id_country_id', '=', self.pol_id_country_id.id),
                  ('pod_id_country_id', '=', self.pod_id_country_id.id),
                  ('expiration_date', '>', fields.Date.today())]

        # If transport_type_id is not 1, add the shipment_scope_id filter
        if self.transport_type_id.id != 1:
            domain.append(('shipment_scope_id', '=', self.shipment_scope_id.id))

        available_prices = self.env['product.template'].search(domain)
        pricing_stage = self.env['crm.stage'].search([('is_pricing_stage', '=', True)])
        self.stage_id = pricing_stage.id

        if available_prices:
            self.show_request_price = False
            followup_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
            if not followup_stage:
                raise UserError("No Follow up stage found in the system. Please create one.")
            self.stage_id = followup_stage.id
            self.show_send_email = True
            self.write({
                'crm_available_prices': [
                    (5, 0, 0),  # Removes all existing records
                    *[(0, 0, {'product_id': price.id}) for price in available_prices]  # Insert new records
                ]
            })
            if show_message:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Rates Available'),
                        'message': _('Please check the tab below and quote your customer shortly.'),
                        'type': 'info',
                        'sticky': False,
                        'next': {
                            'type': 'ir.actions.client',
                            'tag': 'soft_reload',
                        },
                    },
                }

        else:
            if show_message:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Error'),
                        'message': _('No available prices found for the selected criteria.'),
                        'type': 'danger',
                        'sticky': False,
                    }
                }

    def action_move_followup(self):
        pricing_stage = self.env['crm.stage'].search([('is_follow_up_stage', '=', True)])
        self.stage_id = pricing_stage.id

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
                'email_to': ','.join(email_list),
            }
            mail_template.sudo().send_mail(self.id, force_send=True, email_values=email_values)
            self.show_send_email = False

        return True

    def action_open_pricing_opportunities(self):

        return {
            'name': 'Opportunities',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'kanban,tree,graph,pivot,form,calendar,activity',
            'views': [
                (self.env.ref('eit_freight_workflow.view_crm_lead_kanban_pricing').id, 'kanban'),
                (self.env.ref('crm.crm_case_tree_view_oppor').id, 'tree'),
            ],
            'domain': ['|', ('type', '=', 'opportunity'), ('stage_id.is_won', '=', False)],
            'context': {
                'create': False,
                'hide_create_rfq_button': False,
            },
        }

    def action_mark_lost(self):
        if self.quotation_count > 0:
            action = self.env.ref('eit_freight_workflow.action_confirm_message_wizard').read()[0]
            quotations = self.order_ids.filtered_domain([('state', 'in', ('draft', 'sent'))])
            return {
                'name': 'Confirm Message',
                'type': 'ir.actions.act_window',
                'res_model': 'confirm.message.wizard',
                'view_mode': 'form',
                'view_id': self.env.ref('eit_freight_workflow.view_confirm_message_wizard_form').id,
                'target': 'new',
                'context': {
                    'default_name': 'Confirmation',
                    'default_message': 'There are some quotations, Are you sure you want to proceed?',
                    'default_confirm_message': ', '.join([f'{quote.name}' for quote in quotations]),
                    'default_show_label': False,
                    'active_id': self.id,  # Pass the active sale order ID
                }
            }
        action = self.env.ref('crm.crm_lead_lost_action').read()[0]
        # You can modify the context if needed, like passing active_ids or other parameters
        action['context'] = {
            'dialog_size': 'medium',
            'default_lead_ids': self.ids  # Pass current record's ID or a list of IDs
        }
        return action

    def open_confirm_message_wizard(self):
        # Trigger the confirmation wizard action
        return {
            'name': 'Confirm Message',
            'type': 'ir.actions.act_window',
            'res_model': 'confirm.message.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('your_module.view_confirm_message_wizard_form').id,
            'target': 'new',
            'context': {
                'default_name': 'Confirmation',
                'default_message': 'Are you sure you want to proceed?',
                'active_id': self.id,  # Pass the active sale order ID
            }
        }