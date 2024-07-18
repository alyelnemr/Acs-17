from odoo import models, fields


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2many('partner.type', string="Partner Type", required=True)
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user.id, string="Created by", readonly=True)
    excecuters = fields.Many2many('res.users', string="Executors")
    # show_partner = fields.Boolean()
