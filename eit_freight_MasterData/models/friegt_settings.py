# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, _, models, api
from odoo.exceptions import UserError


class FreightType(models.Model):
    _name = "transport.type"
    _description = 'Transport Type Data'
    _order = 'id asc'

    name = fields.Char(string="Name")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status', readonly=True)
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Active', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class PackageType(models.Model):
    _name = "package.type"
    _description = 'Package Type Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    type = fields.Selection([('air', 'Air'), ('lcr', 'LCR')], 'Is')
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status', readonly=True)
    active = fields.Boolean(string='Active', default=True)
    tag_type_ids = fields.Many2many('package.tag.type', string="Package Is")

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class ContainerType(models.Model):
    _name = "container.type"
    _description = 'Container Type Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    container_type = fields.Selection([('dry', 'Dry'), ('reefer', 'Reefer'), ('sequ', 'Special Equ')], 'Type Is')
    size = fields.Float(string="Size")
    volume = fields.Float(string="Volume")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status', readonly=True)
    active = fields.Boolean(string='Active', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class ShipmentScop(models.Model):
    _name = "shipment.scop"
    _description = 'Ocean shipments scope Data'
    _order = 'id desc'

    name = fields.Char(string="Name", readonly=True)
    code = fields.Char(string="Code", readonly=True)
    type = fields.Selection([('sea', 'Sea'), ('inland', 'Inland')], 'Type', readonly=True)


class Vessels(models.Model):
    _name = "fright.vessels"
    _description = 'Vessels Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    partner_id = fields.Many2one('res.partner', string="Vessel Owner")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active', readonly=True)
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class ContainerData(models.Model):
    _name = "container.data"
    _description = 'Container Data'
    _order = 'id desc'

    container_id = fields.Many2one('container.type', string="Container Type")
    name = fields.Char(string="Container Number")
    container_type = fields.Selection([('dry', 'Dry'), ('reefer', 'Reefer'), ('sequ', 'Special Equ')], 'Container Is')
    partner_id = fields.Many2one('res.partner', string="Container Owner")
    tare_weight = fields.Float(string="Tare Weight")
    max_load = fields.Float(string="Max Load")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Status')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string="Description")
    carrier_seal = fields.Text(string="Carrier Seal")
    net_wt = fields.Float(string="NetWt(KG)")
    vol_cbm = fields.Integer(string="Vol.(CBM)")
    gross_weight = fields.Float(string="Gross(KG)")
    vkm = fields.Float(string="VGM(KG)")
    temperature = fields.Integer(string="Temperature")
    un_number = fields.Many2many('ir.attachment', string="UN Number")
    pacchage_line_ids = fields.One2many('package.line', 'shipping_container_id', string="Packages")
    number_of_packages = fields.Integer(string="Number Of Packages")
    task_id_container = fields.Many2one('project.task')

    _sql_constraints = [('name_uniq', "unique(name)",
                         "This Container Has Been Added Before")]

    @api.onchange('pacchage_line_ids')
    def onchange_pacchage_line_ids(self):
        self.number_of_packages = len(self.pacchage_line_ids)

    @api.onchange('gross_weight')
    def _onchange_gross_weight(self):
        self.vkm = self.gross_weight + self.tare_weight

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, '%s' % (rec.name)))
        return result

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()

    @api.onchange('name')
    def _onchange_container_number(self):
        if self.name:
            input_string = self.name
            result = "True"
            if len(input_string) != 11:
                result = "False"

            if not input_string[:3].isalpha() or not input_string[:3].isupper():
                result = "False"

            if input_string[3] != 'U':
                result = "False"

            if not input_string[4:].isdigit():
                result = "False"
            if result == "False":
                raise UserError(
                    _("The number should contain 4 Capital letters Must ended By (U) & 7 numbers"))


class Flights(models.Model):
    _name = "frieght.flights"
    _description = 'Flights Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    partner_id = fields.Many2one('res.partner', string="Airline")
    status = fields.Selection([('active', 'Active'), ('inactive', 'Inactive')], 'Active')
    active = fields.Boolean(string='Status', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class BillofLeading(models.Model):
    _name = "bill.leading.type"
    _description = 'BOL Type Data'
    _order = 'id desc'

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
    active = fields.Boolean(string='Active', default=True)

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()


class PackageType(models.Model):
    _name = "package.tag.type"
    _description = 'Package Tag Type Data'

    name = fields.Char()


class PackageLine(models.Model):
    _name = "package.line"

    commodity_data_id = fields.Many2one('commodity.data', string="Commodity")
    package_type_id = fields.Many2one('package.type', string="Package Type")
    quantity = fields.Integer(string="Quantity")
    gw = fields.Integer(string="GW")
    cbm = fields.Integer(string="CBM")
    shipping_container_id = fields.Many2one('container.data')
