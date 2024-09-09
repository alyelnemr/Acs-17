from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class TotalCostCurrency(models.Model):
    _name = 'total.cost.currency'
    _description = "Total cost currency"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_cost = fields.Many2one('product.template')
