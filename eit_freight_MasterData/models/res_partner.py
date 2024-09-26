from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2many('partner.type', string="Partner Type", required=True)
    excecuters = fields.Many2many('res.users', string="Executors")
    show_vendor_portal = fields.Boolean(string="Show Vendor Portal", default=False)
    vendor_portal_ids = fields.One2many(comodel_name='vendor.portal', inverse_name='partner_id', string='vendor_portal_id')
    partner_type_id_1 = fields.Many2many('partner.type', string="Partner Type1", compute="compute_partner_type_id_1")
    carrier_route_ids = fields.One2many('carrier.route', 'partner_id', string="Carriers")
    carrier_route_count = fields.Integer(
        string="Carrier Routes Count",
        compute='_compute_carrier_route_count'
    )

    @api.depends('carrier_route_ids')
    def _compute_carrier_route_count(self):
        for partner in self:
            # Count the number of carrier routes where the partner is in the carriers Many2many field
            partner.carrier_route_count = self.env['carrier.route'].search_count([('carrier_ids', 'in', partner.id)])

    def action_view_carrier_routes(self):
        """Action to open the carrier routes related to this partner."""
        self.ensure_one()
        return {
            'name': 'Carrier Routes',
            'domain': [('carriers', 'in', self.id)],
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'carrier.route',
            'type': 'ir.actions.act_window',
            'context': {'default_carrier_ids': [(4, self.id)]},
        }

    @api.model
    def create(self, vals):
        partner = super(InheritResPartner, self).create(vals)
        partner._add_executors_as_followers()
        return partner

    def write(self, vals):
        result = super(InheritResPartner, self).write(vals)
        self._add_executors_as_followers()
        return result

    def _add_executors_as_followers(self):
        for partner in self:
            if partner.excecuters:
                # Check if the executors are already in the message_follower_ids
                current_followers = partner.message_follower_ids.mapped('partner_id').ids
                new_followers = partner.excecuters.mapped('partner_id').filtered(
                    lambda p: p.id not in current_followers)

                # Add new executors as followers
                if new_followers:
                    partner.message_subscribe(new_followers.ids)

    def compute_partner_type_id_1(self):
        for rec in self:
            if rec.parent_id:
                parent = self.search([('id', '=', rec.parent_id.id)])
                if parent and parent.company_type == "company" and parent.partner_type_id:
                    rec.partner_type_id_1 = parent.partner_type_id.ids
                else:
                    rec.partner_type_id_1 = None
            else:
                rec.partner_type_id_1 = None

    # def show_partner_reset(self):
    #     part = self.search([('show_partner', '=', True)])
    #     for p in part:
    #         p.show_partner = False

    @api.model
    def create(self, vals_list):
        res = super(InheritResPartner, self).create(vals_list)

        # partner_types_to_add = []
        #
        # sale_order = self.env['sale.order'].search([('partner_id', '=', res.id), ('website_id', '!=', False)], limit=1)
        # if sale_order:
        #     partner_type_14 = self.env.ref('eit_freight_MasterData.partner_type_14')
        #     if partner_type_14:
        #         partner_types_to_add.append((4, partner_type_14.id))
        #
        # employee = self.env['hr.employee'].search([('address_home_id', '=', res.id)], limit=1)
        # if employee:
        #     partner_type_8 = self.env.ref('eit_freight_MasterData.partner_type_8')
        #     if partner_type_8:
        #         partner_types_to_add.append((4, partner_type_8.id))
        #
        # applicant = self.env['hr.applicant'].search([('partner_id', '=', res.id)], limit=1)
        # if applicant:
        #     partner_type_9 = self.env.ref('eit_freight_MasterData.partner_type_9')
        #     if partner_type_9:
        #         partner_types_to_add.append((4, partner_type_9.id))
        #
        # portal_group = self.env.ref('base.group_portal')
        # portal_user = self.env['res.users'].search([('partner_id', '=', res.id), ('groups_id', 'in', portal_group.id)], limit=1)
        # if portal_user:
        #     partner_type_14 = self.env.ref('eit_freight_MasterData.partner_type_14')
        #     if partner_type_14:
        #         partner_types_to_add.append((4, partner_type_14.id))
        #
        # internal_group = self.env.ref('base.group_user')  # This is the "Internal User" group
        # internal_user = self.env['res.users'].search([('partner_id', '=', res.id), ('groups_id', 'in', internal_group.id)], limit=1)
        # if internal_user:
        #     partner_type_8 = self.env.ref('eit_freight_MasterData.partner_type_8')
        #     if partner_type_8:
        #         partner_types_to_add.append((4, partner_type_8.id))
        #
        # if partner_types_to_add:
        #     res.partner_type_id = partner_types_to_add

        return res


class VendorsPortal(models.Model):
    _name = "vendor.portal"

    url = fields.Char(string="Portal URL")
    username = fields.Char(string="Portal Username")
    password = fields.Char(string="Portal Password")
    partner_id = fields.Many2one(comodel_name='res.partner', string="Vendor")
