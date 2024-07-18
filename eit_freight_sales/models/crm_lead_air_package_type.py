from odoo import models, fields, api, tools


class CrmLeadAirPackageType(models.Model):
    _name = 'crm.lead.air.package.type'
    _description = 'CRM Lead AIR Package Type'

    lead_id = fields.Many2one('crm.lead', string="Lead", store=True)
    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True, domain="[('tag_type_ids', 'in', [2])]", onchange=True)
    qty = fields.Float(string="QTY", store=True)
    gw_kg = fields.Float(string="GW (KG)", store=True)
    length_cm = fields.Float(string="L (CM)", store=True)
    width_cm = fields.Float(string="W (CM)", store=True)
    height_cm = fields.Float(string="H (CM)", store=True)
    cbm = fields.Float(string="CBM")
    vm = fields.Float(string="VM", compute='_compute_vm', store=True)
    chw = fields.Float(string="CHW", compute="compute_chw", store=True)
    volume = fields.Float(string='Volume')
    weight = fields.Float(string='Weight')

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
