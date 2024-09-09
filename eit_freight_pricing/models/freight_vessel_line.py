from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class FreightVesselLine(models.Model):
    _name = 'frieght.vessel.line'

    vessel_id = fields.Many2one('freight.vessels', string="Vessel")
    voyage_number = fields.Char(string="Voyage Number")
    etd = fields.Date(string="ETD")
    eta = fields.Date(string="ETA")
    tt_day = fields.Integer(string="T.T Day")
    product_vessel_id = fields.Many2one('product.template')

    @api.onchange('tt_day')
    def _compute_eta(self):
        for record in self:
            if record.etd and record.tt_day:
                etd_date = fields.Date.from_string(record.etd)
                eta_date = etd_date + timedelta(days=record.tt_day)
                record.eta = fields.Date.to_string(eta_date)

    @api.onchange('eta')
    def _compute_tt_day(self):
        for record in self:
            if record.etd and record.eta:
                etd_date = fields.Date.from_string(record.etd)
                eta_date = fields.Date.from_string(record.eta)
                delta = eta_date - etd_date
                record.tt_day = delta.days
