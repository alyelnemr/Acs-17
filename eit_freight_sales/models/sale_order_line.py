from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    package_type = fields.Many2one('package.type', string="Package Type")
    container_type = fields.Many2one('container.type', string="Container Type")
    unit_rate = fields.Monetary(string="Unit Rate")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    main_curr = fields.Monetary(string="Main Currency", compute='_compute_tot_price')
    main_currency_id = fields.Many2one(comodel_name='res.currency', compute='_compute_main_currency_id', string="Main Currency", store=True)
    technical_rate = fields.Float(string="Technical Rate", compute="compute_technical_rate")

    @api.depends('order_id.pricelist_id', 'company_id')
    def _compute_main_currency_id(self):
        for line in self:
            line.main_currency_id = line.order_id.pricelist_id.currency_id or line.order_id.company_id.currency_id

    @api.depends('currency_id')
    def compute_technical_rate(self):
        for rec in self:
            currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
            if currency_id:
                rec.technical_rate = currency_id.rate_ids[0].company_rate if currency_id.rate_ids else 1.0

    @api.depends('ex_rate', 'unit_rate', )
    def _compute_tot_price(self):
        for rec in self:
            rec.main_curr = rec.ex_rate * rec.unit_rate * rec.product_uom_qty

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0 or (line.product_id.expense_policy == 'cost' and line.is_expense):
                continue
            if not line.product_uom or not line.product_id:
                line.price_unit = 0.0
            elif line.order_id.website_id:
                line.price_unit = line.product_id.uom_id._compute_price(
                    line.product_id.list_price, line.product_uom
                )
            else:
                line = line.with_company(line.company_id)
                price = line._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price_from_price(
                    price,
                    line.currency_id or line.order_id.currency_id,
                    product_taxes=line.product_id.taxes_id.filtered(
                        lambda tax: tax.company_id == line.env.company
                    ),
                    fiscal_position=line.order_id.fiscal_position_id,
                )
