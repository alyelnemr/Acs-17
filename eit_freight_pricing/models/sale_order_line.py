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

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.order_id.website_id:
                price_unit = line.product_id.list_price
                price_subtotal = 0
                is_fixed_charge = False
                total_fixed_charge = 0
                for charge in line.product_id.product_tmpl_id.pricing_charge_ids:
                    if charge.product_id_2.product_variant_id.calculation_type == 'fixed_charge':
                        price_unit -= charge.sale_price
                        total_fixed_charge += charge.sale_usd
                        is_fixed_charge = True
                if is_fixed_charge:
                    line.price_subtotal = price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
                    line.price_subtotal += total_fixed_charge
                else:
                    line.price_subtotal = line.price_unit * line.product_uom_qty * (1 - (line.discount or 0.0) / 100.0)
            else:
                tax_results = self.env['account.tax'].with_company(line.company_id)._compute_taxes([
                    line._convert_to_tax_base_line_dict()
                ])
                totals = list(tax_results['totals'].values())[0]
                amount_untaxed = totals['amount_untaxed']
                amount_tax = totals['amount_tax']

                line.update({
                    'price_subtotal': amount_untaxed,
                    'price_tax': amount_tax,
                    'price_total': amount_untaxed + amount_tax,
                })