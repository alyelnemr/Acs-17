from odoo import fields, _, models, api
from odoo.exceptions import UserError


class ShippingContainerData(models.Model):
    _name = "shipping.container"
    _description = 'Shipping Container Data'
    _order = 'id desc'

    container_id = fields.Many2one(comodel_name='container.data', string="Container")
    name = fields.Char(string="Container Number", required=True)
    container_type_id = fields.Many2one(comodel_name='container.type', string="Container Type")
    container_is = fields.Selection(selection=[('dry', 'Dry'), ('reefer', 'Reefer'), ('sequ', 'Special Equ')],
                                    string='Container Is', required=True)
    container_owner_id = fields.Many2one('res.partner', string="Container Owner")
    tare_weight = fields.Float(string="Tare Weight")
    max_load = fields.Float(string="Max Load")
    status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], string='Status')
    active = fields.Boolean(string='Active', default=True)
    description = fields.Text(string="Description")
    carrier_seal = fields.Text(string="Carrier Seal")
    net_wt = fields.Float(string="NetWt(KG)")
    vol_cbm = fields.Integer(string="Vol.(CBM)")
    gross_weight = fields.Float(string="Weight (KG)")
    vkm = fields.Float(string="VGM(KG)")
    temperature = fields.Integer(string="Temperature")
    un_number = fields.Many2many('ir.attachment', string="UN Number")
    package_line_ids = fields.One2many('shipping.container.details', 'shipping_container_id', string="Packages")
    number_of_packages = fields.Integer(string="Number Of Packages")
    loading_instruction = fields.Html(string="Loading Instructions")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Task")

    @api.onchange('package_line_ids')
    def onchange_package_line_ids(self):
        self.number_of_packages = len(self.package_line_ids)

    @api.onchange('gross_weight')
    def _onchange_gross_weight(self):
        self.vkm = self.gross_weight + self.tare_weight

    @api.onchange('active')
    def _onchange_active(self):
        for rec in self:
            if not rec.active:
                rec.toggle_active()

    def create(self, vals_list):
        for vals in vals_list:
            if self.check_container_number(vals['name']):
                # Call super to create the record
                res = super(ShippingContainerData, self).create(vals)

                # Search for the existing container data record
                container_id = self.env['container.data'].search([('name', '=', res.name)], limit=1)

                if container_id:
                    # If the container already exists, update it
                    container_id.write({
                        'container_type_id': vals.get('container_type_id', res.container_type_id.id),
                        'container_is': vals.get('container_is', res.container_is),
                        'tare_weight': vals.get('tare_weight', res.tare_weight),
                    })
                    # Set the container_id on the new record
                    res.container_id = container_id.id
                else:
                    # If the container doesn't exist, create a new one
                    new_container_id = self.env['container.data'].sudo().create({
                        'name': vals.get('name', res.name),
                        'container_type_id': vals.get('container_type_id', res.container_type_id.id),
                        'container_is': vals.get('container_is', res.container_is),
                        'tare_weight': vals.get('tare_weight', res.tare_weight),
                    })
                    # Set the container_id on the new record
                    res.container_id = new_container_id.id

                return res

    def write(self, vals):
        for record in self:
            res = super(ShippingContainerData, self).write(vals)
            container_id = self.env['container.data'].search([('name', '=', record.name)], limit=1)
            if container_id:
                container_id.write({
                    'container_type_id': vals.get('container_type_id', record.container_type_id.id),
                    'container_is': vals.get('container_is', record.container_is),
                    'tare_weight': vals.get('tare_weight', record.tare_weight),
                })
                vals['container_id'] = container_id.id
            else:
                new_container_id = self.env['container.data'].create({
                    'name': vals.get('name', record.name),
                    'container_type_id': vals.get('container_type_id', record.container_type_id.id),
                    'container_is': vals.get('container_is', record.container_is),
                    'tare_weight': vals.get('tare_weight', record.tare_weight),
                })
                vals['container_id'] = new_container_id.id
            return res

    @api.onchange('name')
    def _onchange_container_number(self):
        if self.check_container_number():
            container_id = self.env['container.data'].search([('name', '=', self.name)], limit=1)
            if container_id:
                self.container_type_id = container_id.container_type_id
                self.container_is = container_id.container_is
                self.container_id = container_id.id

    def check_container_number(self, name=None):
        container_name = self.name or name
        show_error = False
        if container_name:
            input_string = container_name
            if len(input_string) != 11:
                show_error = True
            elif input_string[3] != 'U':
                show_error = True
            elif not input_string[:3].isalpha() or not input_string[:3].isupper():
                show_error = True
            elif not input_string[4:].isdigit():
                show_error = True
        if show_error:
            raise UserError("The number should contain 4 Capital letters Must ended By (U) & 7 numbers")
        else:
            return True


class PackageLine(models.Model):
    _name = "shipping.container.details"
    _description = "Shipping Container Details"

    commodity_data_id = fields.Many2one('commodity.data', string="Commodity")
    package_type_id = fields.Many2one('package.type', string="Package Type")
    quantity = fields.Integer(string="Quantity")
    gw = fields.Integer(string="GW")
    cbm = fields.Integer(string="CBM")
    shipping_container_id = fields.Many2one('shipping.container')
