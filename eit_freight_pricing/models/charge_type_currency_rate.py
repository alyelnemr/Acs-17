from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ChargeTypeCurrencyRate(models.Model):
    _name = 'charge.type.currency.rate'
    _description = "Charge Type Currency Rate"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    charge_id = fields.Many2one('product.charges', string="Charge")
    purchase_id = fields.Many2one('purchase.order', string="Purchase Order")

    # @api.depends('transport_type')
    # def _compute_pol_domain(self):
    #     for record in self:
    #         if record.purchase_id.transport_type_id.name == 'Air':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_11').id])]

    #         elif record.purchase_id.transport_type_id.id in 'Air':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_12').id])]

    #         elif record.transport_type.name == 'In-land':
    #             record.dyn_filter_par = [('partner_type_id', 'in', [record.env.ref('frieght.partner_type_5').id])]

    #         else:
    #             record.dyn_filter_par = [('id', 'in', [])]
