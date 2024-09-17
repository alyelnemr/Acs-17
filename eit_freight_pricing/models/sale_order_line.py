# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _prepare_order_line_update_values(
        self, order_line, quantity, linked_line_id=False, **kwargs
    ):
        values = super(SaleOrder, self)._prepare_order_line_update_values(
            order_line, quantity, linked_line_id, **kwargs
        )
        currency_usd_id = self.env['res.currency'].search([('name', '=', 'USD')], limit=1)
        values['price_unit'] = order_line.product_id.list_price
        values['currency_id'] = currency_usd_id.id
        return values

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_displayed_unit_price(self):
        show_tax = self.order_id.website_id.show_line_subtotals_tax_selection
        tax_display = 'total_excluded' if show_tax == 'tax_excluded' else 'total_included'

        return self.tax_id.compute_all(
            self.product_id.list_price, self.currency_id, 1, self.product_id, self.order_partner_id,
        )[tax_display]
