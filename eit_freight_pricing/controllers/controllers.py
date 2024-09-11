from odoo import models
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression
from odoo import http
from odoo.http import request
from odoo.addons.website_sale.controllers.variant import WebsiteSaleVariantController


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
