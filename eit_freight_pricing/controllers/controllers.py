from odoo import fields, models, SUPERUSER_ID
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression
from odoo.addons.payment import utils as payment_utils
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.exceptions import ValidationError


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
        request.session['website_sale_shop_layout_mode'] = 'list'
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

    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.provider. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.provider website but closed the tab without
           paying / canceling
        """
        order = request.website.sale_get_order()
        order.only_services = True
        partner_type = request.env.ref('eit_freight_MasterData.partner_type_14')

        order.partner_id.partner_type_id = [(4, partner_type.id, 0)]

        if order and not order.only_services and (request.httprequest.method == 'POST' or not order.carrier_id):
            # Update order's carrier_id (will be the one of the partner if not defined)
            # If a carrier_id is (re)defined, redirect to "/shop/payment" (GET method to avoid infinite loop)
            carrier_id = post.get('carrier_id')
            keep_carrier = post.get('keep_carrier', False)
            if keep_carrier:
                keep_carrier = bool(int(keep_carrier))
            if carrier_id:
                carrier_id = int(carrier_id)
            order._check_carrier_quotation(force_carrier_id=carrier_id, keep_carrier=keep_carrier)
            if carrier_id:
                return request.redirect("/shop/payment")

        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('payment_methods_sudo', '')
            render_values.pop('tokens_sudo', '')

        # return request.render("website_sale.payment", render_values)
        return request.redirect("/shop/payment/validate")

    @http.route('/shop/payment/validate', type='http', auth="public", website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        """ Inherit and modify the validation to use a fake transaction """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')

        errors = self._get_shop_payment_errors(order)
        if errors:
            first_error = errors[0]  # only display first error
            error_msg = f"{first_error[0]}\n{first_error[1]}"
            raise ValidationError(error_msg)
        payment_method_id = request.env['payment.method'].with_context(active_test=False).search([], limit=1)
        # Replace the transaction fetching logic with a fake transaction record
        tx_sudo = request.env['payment.transaction'].sudo().create({
            'provider_id': request.env['payment.provider'].search([], limit=1).id,
            'amount': order.amount_total,
            'currency_id': order.currency_id.id,
            'partner_id': order.partner_id.id,
            'sale_order_ids': [(6, 0, [order.id])],
            'reference': order.name,
            'state': 'done',  # Fake transaction set to 'done'
            'payment_method_id': payment_method_id.id,
        })

        if not order or (order.amount_total and not tx_sudo):
            return request.redirect('/shop')

        if order and tx_sudo:
            if order.state != 'sale':
                order.with_context(send_email=True).with_user(SUPERUSER_ID).action_confirm()
            request.website.sale_reset()
            return request.redirect(order.get_portal_url())

        # Clean context and session, then redirect to the confirmation page
        request.website.sale_reset()
        if tx_sudo and tx_sudo.state == 'draft':
            return request.redirect('/shop')

        return request.redirect('/shop/confirmation')
