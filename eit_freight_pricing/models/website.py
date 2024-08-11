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