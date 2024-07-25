from odoo import models, fields, api


class InheritResPartner(models.Model):
    _inherit = "res.partner"

    partner_type_id = fields.Many2many('partner.type', string="Partner Type", required=True)
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

    def show_partner_reset(self):
        part = self.search([('show_partner', '=', True)])
        for p in part:
            p.show_partner = False
    def create(self, vals_list):
        for vals in vals_list:
            if 'parent_id' in vals:
                if isinstance(vals['parent_id'], int):  # Check if parent_id is an int
                    parent = self.search([('id', '=', vals['parent_id'])])
                    if parent and parent.company_type == 'company':
                        vals['partner_type_id'] = [(6, 0, parent.partner_type_id.ids)]
                else:
                    raise ValueError(f"parent_id must be an integer, got {type(vals['parent_id'])}")
        return super(InheritResPartner, self).create(vals_list)

    def write(self, vals):
        if 'parent_id' in vals or self.parent_id:
            parent_id = vals['parent_id'] if 'parent_id' in vals else self.parent_id.id or False
            parent = self.search([('id', '=', parent_id)]) if parent_id else False
            if parent and parent.company_type == 'company':
                vals['partner_type_id'] = [(6, 0, parent.partner_type_id.ids)]
        return super(InheritResPartner, self).write(vals)
