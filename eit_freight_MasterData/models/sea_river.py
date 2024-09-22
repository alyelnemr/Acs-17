from odoo import fields, models, api


class SeaRiver(models.Model):
    _name = 'sea.river'
    _description = 'Seas and Rivers'

    name = fields.Char(string='Name', required=True)
    ocean_id = fields.Many2one(comodel_name='ocean.data', string='Ocean', required=True)
