# -*- coding: utf-8 -*-
# from odoo import http


# class EitFreightPricing(http.Controller):
#     @http.route('/eit_freight_pricing/eit_freight_pricing', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/eit_freight_pricing/eit_freight_pricing/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('eit_freight_pricing.listing', {
#             'root': '/eit_freight_pricing/eit_freight_pricing',
#             'objects': http.request.env['eit_freight_pricing.eit_freight_pricing'].search([]),
#         })

#     @http.route('/eit_freight_pricing/eit_freight_pricing/objects/<model("eit_freight_pricing.eit_freight_pricing"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('eit_freight_pricing.object', {
#             'object': obj
#         })

