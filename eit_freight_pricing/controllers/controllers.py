from odoo import models
from odoo import http
from odoo.addons.payment.controllers import portal as payment_portal
from odoo.osv import expression


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
        return super(WebsiteSale, self).shop(page=page, category=category, search=search,
                                             min_price=min_price, max_price=max_price, ppg=ppg, **post)
