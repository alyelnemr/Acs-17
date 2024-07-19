from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2many('partner.type', string="Partner Type", required=True)
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Created by", readonly=True)
    excecuters = fields.Many2many('res.users', string="Executors")
    partner_type_id_1 = fields.Many2many('partner.type', string="Partner Type", compute="compute_partner_type_id_1")

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

    def show_partner_llllll(self):
        part = self.search([('show_partner', '=', False)])
        for p in part:
            p.show_partner = True

    def show_partner_reset(self):
        part = self.search([('show_partner', '=', True)])
        for p in part:
            p.show_partner = False
