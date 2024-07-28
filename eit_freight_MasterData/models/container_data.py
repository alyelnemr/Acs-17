from odoo import fields, _, models, api
from odoo.exceptions import UserError


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
    status = fields.Selection(selection=[('active', 'Active'), ('inactive', 'Inactive')], string='Status')
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
    create_date = fields.Datetime(string='Create Date', readonly=True, default=fields.Datetime.now)

    _sql_constraints = [('name_uniq', "unique(name)", "This Container Has Been Added Before")]

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
