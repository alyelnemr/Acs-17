from odoo import models, fields, api, _


class OptDocuments(models.Model):
    _name = "opt.documents"

    document_type_id = fields.Many2one('document.type', string="Document Name")
    document_no = fields.Integer(string="Document No")
    description = fields.Text(string="Description")
    rec_date = fields.Date(string="Rec.Date")
    attachment_id = fields.Many2many('ir.attachment', string="Upload Doc")
    document_task_id = fields.Many2one('project.task')
    document_service_id = fields.Many2one('origin.services')


class OptPayable(models.Model):
    _name = "opt.payable"

    vendor_name = fields.Many2one('res.partner', string="Vendor Name")
    product_id = fields.Many2one('product.template', string="Charges",
                                 domain="['|',('purchase_ok', '=', True),('can_be_expensed', '=', True)]")
    qty = fields.Float(string="QTY")
    type_1 = fields.Many2one('container.type', string="Container Type")
    type_2 = fields.Many2one('package.type', string="Package Type")
    cost_price = fields.Float(string="Cost Price")
    tax_id = fields.Many2one('account.tax', string="VAT")
    currency = fields.Many2one('res.currency', string="Currency")
    total = fields.Float(string="Total", compute="compute_total")
    payble_route_id = fields.Many2one('origin.services')

    @api.depends('cost_price', 'qty', 'tax_id')
    def compute_total(self):
        for rec in self:
            if rec.qty and rec.cost_price and rec.tax_id:
                rec.total = rec.qty * rec.cost_price * rec.tax_id.amount
            else:
                rec.total = 0


class OptRecieveble(models.Model):
    _name = "opt.recieveble"

    vendor_name = fields.Many2one('res.partner', string="Vendor Name")
    product_id = fields.Many2one('product.template', string="Charges",
                                 domain="['|',('purchase_ok', '=', True),('can_be_expensed', '=', True)]")
    qty = fields.Float(string="QTY")
    type_1 = fields.Many2one('container.type', string="Container Type")
    type_2 = fields.Many2one('package.type', string="Package Type")
    sell_price = fields.Float(string="Sell Price")
    tax_id = fields.Many2one('account.tax', string="VAT")
    currency = fields.Many2one('res.currency', string="Currency")
    total = fields.Float(string="Total", compute="compute_total")
    reciveble_route_id = fields.Many2one('origin.services')

    @api.depends('sell_price', 'qty', 'tax_id')
    def compute_total(self):
        for rec in self:
            if rec.qty and rec.sell_price and rec.tax_id:
                rec.total = rec.qty * rec.sell_price * rec.tax_id.amount
            else:
                rec.total = 0


class Friegtservicestage(models.Model):
    _name = "frieght.serviice.stages"

    stage_id = fields.Many2one('tracking.stage', string="Stage")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    description = fields.Text(string="Description")
    servicestage_route_id = fields.Many2one('origin.services')
