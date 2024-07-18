from odoo import models, fields, api, tools


class CrmLeadAirPackageType(models.Model):
    _name = 'crm.lead.air.package.type'
    _description = 'CRM Lead AIR Package Type'

    @api.model
    def _get_package_type_domain(self):
        # Search for records containing the specific value
        all_records = self.env['package.type'].sudo().search(
            [('tag_type_ids', 'in', [2])]
        )

        # Filter the records to only include those where tag_type_ids is exactly [2]
        filtered_records = all_records.filtered(lambda r: r.tag_type_ids.ids == [2])

        # Return the domain for the Many2one field
        return [('id', 'in', filtered_records.ids)]

    lead_id = fields.Many2one('crm.lead', string="Lead", store=True)
    package_type_id = fields.Many2one(
        'package.type', string="Package Type", store=True, domain=lambda self: self._get_package_type_domain(),
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
            cbm = (rec.length_cm * rec.width_cm * rec.height_cm) / 1000
            rec.cbm = cbm * rec.qty

    @api.depends('length_cm', 'width_cm', 'height_cm')
    def _compute_vm(self):
        for rec in self:
            rec.vm = (rec.length_cm * rec.width_cm * rec.height_cm) / 6000
