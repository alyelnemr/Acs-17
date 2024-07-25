# # -*- coding: utf-8 -*-
#
from odoo import models, fields, api, _
# import datetime
# from odoo.exceptions import ValidationError
# from datetime import timedelta
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    detailed_type = fields.Selection(
        selection_add=[('charge_type', 'Charge Type')],
        ondelete={'charge_type': 'set default'})
    type = fields.Selection(
        selection_add=[('charge_type', 'Charge Type')])
    is_sale_purchase = fields.Boolean()

    @api.model
    def create(self, values):
        res = super(ProductTemplate, self).create(values)

        if res.detailed_type == 'charge_type' and res.is_sale_purchase:
            raise UserError(
                _('Please add the Charge Type from the MasterData App \n Master Data >> Service Setting Menu >> Charge Type'))

        return res

    def write(self, vals):
        is_sale_purchase = self.env.context.get('default_is_sale_purchase', False)

        if vals.get('detailed_type') == 'charge_type' and is_sale_purchase:
            raise UserError(
                _('Please add the Charge Type from the MasterData App \n Master Data >> Service Setting Menu >> Charge Type'))

        result = super(ProductTemplate, self).write(vals)
        return result
