from odoo import models, fields, api


class ShippingPackages(models.Model):
    _name = "shipping.package"
    _description = "Shipping Packages Lines"

    package_type_id = fields.Many2one('package.type', string="Package")
    quantity = fields.Integer(string="Qty")
    length = fields.Float(string="Length")
    width = fields.Float(string="Width")
    height = fields.Float(string="Height")
    volume = fields.Float(string="Volume", )
    net_wight = fields.Float(string="NetWt(KG)")
    gross_weight = fields.Float(string="Gross(KG)")
    commodity_id = fields.Many2one('commodity.data', string="Commodity")
    imo = fields.Boolean(string="IMO")
    ref = fields.Boolean(string="REF")
    un_number = fields.Many2many('ir.attachment', string="UN Number")
    task_id_shipping = fields.Many2one('project.task')
    volume_wt = fields.Float(string="VOL WT")
    chw = fields.Float(string="CHW")
    temperature = fields.Integer(string="Temperature")
    loading_instruction = fields.Html(string="Notes")
    shipping_container_id = fields.Many2one('shipping.container.details', string="Container")

    @api.onchange('volume', 'width', 'height', 'length')
    def compute_volume(self):
        for rec in self:
            if rec.length and rec.width and rec.height:
                rec.volume = rec.length * rec.width * rec.height
                rec.volume_wt = (rec.length * rec.width * rec.height) / 6000
            else:
                rec.volume = 0
                rec.volume_wt = 0

    @api.onchange('gross_weight', 'volume_wt')
    def onchange_volume_wt(self):
        if self.volume_wt < self.gross_weight:
            self.chw = self.gross_weight
        else:
            self.chw = self.volume_wt
