from odoo import fields, models
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression
from odoo.addons.payment import utils as payment_utils
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.tools.json import scriptsafe as json_scriptsafe


class Website(models.Model):
    _inherit = 'website'

    def sale_product_domain(self):
        return expression.AND([
            super().sale_product_domain(),
            [('detailed_type', '=', 'pricing')],
        ])


class WebsiteSale(payment_portal.PaymentPortal):

    @http.route([
        '/shop',
        '/shop/page/<int:page>',
        '/shop/category/<model("product.public.category"):category>',
        '/shop/category/<model("product.public.category"):category>/page/<int:page>',
        '/live-shipping-rates',  # Add this new URL
    ], type='http', auth="public", website=True, sitemap='shop')
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        # change the route to /live-shipping-rates
        response = super(WebsiteSale, self).shop(page=page, category=category, search=search,
                                                 min_price=min_price, max_price=max_price, ppg=ppg, **post)

        # Fetch the USD currency (assuming the USD currency has a code 'USD')
        currency_usd_id = request.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        # Update the response values to include 'currency_usd_id'
        response.qcontext.update({
            'currency_usd_id': currency_usd_id,
        })

        return response

    def _prepare_product_values(self, product, category, search, **kwargs):
        returned_dict = super(WebsiteSale, self)._prepare_product_values(product, category, search, **kwargs)

        currency_usd_id = request.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        returned_dict.update({
            'currency_usd_id': currency_usd_id
        })

        return returned_dict

    @http.route(['/shop/cart'], type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        # Get the current order from the website
        order = request.website.sale_get_order()

        # Call the original 'cart' method to retain the existing functionality
        response = super(WebsiteSale, self).cart(access_token=access_token, revive=revive, **post)

        currency_usd_id = request.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        # Adding currency_usd_id to the response values
        values = response.qcontext if hasattr(response, 'qcontext') else {}
        values['currency_usd_id'] = currency_usd_id

        return request.render("website_sale.cart", values)

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
            self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
            product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        """
        This route is called :
            - When changing quantity from the cart.
            - When adding a product from the wishlist.
            - When adding a product to cart on the same page (without redirection).
        """
        order = request.website.sale_get_order(force_create=True)
        if order.state != 'draft':
            request.website.sale_reset()
            if kw.get('force_create'):
                order = request.website.sale_get_order(force_create=True)
            else:
                return {}

        if product_custom_attribute_values:
            product_custom_attribute_values = json_scriptsafe.loads(product_custom_attribute_values)

        if no_variant_attribute_values:
            no_variant_attribute_values = json_scriptsafe.loads(no_variant_attribute_values)

        values = order._cart_update(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            **kw
        )

        values['notification_info'] = self._get_cart_notification_information(order, [values['line_id']])
        values['notification_info']['warning'] = values.pop('warning', '')
        request.session['website_sale_cart_quantity'] = order.cart_quantity

        if not order.cart_quantity:
            request.website.sale_reset()
            return values

        values['cart_quantity'] = order.cart_quantity
        values['minor_amount'] = payment_utils.to_minor_currency_units(
            order.amount_total, order.currency_id
        ),
        values['amount'] = order.amount_total

        if not display:
            return values

        # Add the USD currency to the values
        currency_usd_id = request.env['res.currency'].search([('name', '=', 'USD')], limit=1)

        values['cart_ready'] = order._is_cart_ready()
        values['website_sale.cart_lines'] = request.env['ir.ui.view']._render_template(
            "website_sale.cart_lines", {
                'website_sale_order': order,
                'currency_usd_id': currency_usd_id,
                'date': fields.Date.today(),
                'suggested_products': order._cart_accessories()
            }
        )
        values['website_sale.total'] = request.env['ir.ui.view']._render_template(
            "website_sale.total", {
                'website_sale_order': order,
            }
        )

        return values


class WebsiteSaleVariantControllerInherit(WebsiteSaleVariantController):

    @http.route('/website_sale/get_combination_info', type='json', auth='public', methods=['POST'], website=True)
    def get_combination_info_website(
            self, product_template_id, product_id, combination, add_qty, parent_combination=None, **kwargs
    ):
        # Call the original method from the parent class
        combination_info = super(WebsiteSaleVariantControllerInherit, self).get_combination_info_website(
            product_template_id, product_id, combination, add_qty, parent_combination, **kwargs
        )

        # Custom logic: You can modify or add to combination_info here
        # Example: Add a custom field or perform additional processing
        combination_info['custom_field'] = 'Custom Value'

        # Return the modified combination info
        return combination_info
