from odoo import models, fields, api, _


class StagePricing(models.Model):
    _name = 'stage.pricing'
    _order = 'sequences'
    _rec_name = 'name'

    name = fields.Text(string="Stage")
    sequences = fields.Integer(string="Sequences")
    folded = fields.Boolean(string="Folded")
