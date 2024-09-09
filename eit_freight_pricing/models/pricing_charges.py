from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class ProductCharges(models.Model):
    _name = 'pricing.charges'
    _description = "Pricing Charges"

    product_id_2 = fields.Many2one('product.template', string="Charge Type",
                                   domain="[('detailed_type', '=', 'charge_type')]")
    product_id = fields.Many2one('product.template', string="Charge Type")
    sale_price = fields.Monetary(string="Sale price")
    cost_price = fields.Monetary(string="Cost price")
    qty = fields.Float(string="QTY", default=1)
    package_type = fields.Many2one('package.type', string="Container/Package")
    container_type = fields.Many2one('container.type', string="Container/Package")
    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    sale_main_curr = fields.Float(string="Sale Main Curr", compute='_compute_tot_price')
    sale_usd = fields.Float(string="Sales(USD)",
                            compute='_compute_tot_price')
    cost_main_curr = fields.Float(string="Cost Main Curr", compute='_compute_tot_price')
    cost_usd = fields.Float(string="Cost (USD)",
                            compute='_compute_tot_price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('sale_price', 'ex_rate', 'qty', 'cost_price')
    def _compute_tot_price(self):
        for record in self:
            company_rate = 1.0
            if record.sale_price and record.ex_rate:
                record.sale_main_curr = record.sale_price * record.ex_rate
            else:
                record.sale_main_curr = 0

            if record.ex_rate:
                currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
                if currency_id:
                    company_rate = currency_id.rate_ids[0].company_rate if currency_id.rate_ids else 1.0

                record.cost_main_curr = record.cost_price * record.ex_rate
                record.cost_usd = company_rate * record.cost_main_curr
                record.sale_usd = company_rate * record.sale_main_curr
            else:
                record.cost_main_curr = 0
                record.cost_usd = 0
                record.sale_usd = 0
