from odoo import _, _lt, SUPERUSER_ID, api, fields, models, tools


class Website(models.Model):
    _inherit = 'website'

    account_on_checkout = fields.Selection(
        string="Customer Accounts",
        selection=[
            ('optional', 'Optional'),
            ('disabled', 'Disabled (buy as guest)'),
            ('mandatory', 'Mandatory (no guest checkout)'),
        ],
        default='mandatory')

    def _get_product_page_proportions(self):
        """
        Returns the number of columns (css) that both the images and the product details should take.
        """
        self.ensure_one()

        product_page_image_width = '50_pc' if self.product_page_image_width == 'none' else self.product_page_image_width

        return {
            'none': (0, 12),
            '50_pc': (6, 6),
            '66_pc': (8, 4),
            '100_pc': (12, 12),
        }.get(product_page_image_width)
