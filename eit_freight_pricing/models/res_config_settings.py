from odoo import api, models, fields, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    enabled_extra_checkout_step = fields.Boolean(default=True)
    # group_product_variant = fields.Boolean(default=True)
    # module_sale_product_matrix = fields.Boolean(default=True)

    @api.depends('website_id.account_on_checkout')
    def _compute_account_on_checkout(self):
        for record in self:
            record.account_on_checkout = 'mandatory'

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            enabled_extra_checkout_step=True,
            enabled_buy_now_button=True,
            # group_product_variant=True,
            # module_sale_product_matrix=True
        )
        return res
