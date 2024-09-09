from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class TotalSaleCurrency(models.Model):
    _name = 'total.sale.currency'
    _description = "Total sale currency"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    product_sale = fields.Many2one('product.template')
