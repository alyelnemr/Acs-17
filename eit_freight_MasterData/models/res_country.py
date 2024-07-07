from odoo import fields, models


class Country(models.Model):
    _inherit = 'res.country'
    _order = 'id desc'


class CountryGroup(models.Model):
    _inherit = 'res.country.group'
    _order = 'id desc'
