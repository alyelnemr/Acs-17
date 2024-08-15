from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    purchase_type = fields.Selection([('purchase', 'Purchase'), ('pricing', 'Pricing')], string="Purchase Type",
                                     default='purchase')
