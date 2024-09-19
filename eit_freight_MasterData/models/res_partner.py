from odoo import models, fields, api

class InheritResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2many('partner.type', string="Partner Type", required=True)
    excecuters = fields.Many2many('res.users', string="Executors")
    partner_type_id_1 = fields.Many2many('partner.type', string="Partner Type1", compute="compute_partner_type_id_1")

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

    def show_partner_reset(self):
        part = self.search([('show_partner', '=', True)])
        for p in part:
            p.show_partner = False

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
