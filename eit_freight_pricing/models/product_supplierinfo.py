from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from datetime import timedelta


class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'

    tt_days = fields.Integer(string="T.T Days")
    service_grade = fields.Selection(
        string="Service Grade",
        selection=[('good', 'Good'),
                   ('accept', 'Acceptable'),
                   ('bad', 'Bad'),
                   ('excellent', 'Excellent')
                   ])
    status = fields.Selection(
        string="Status",
        selection=[('weekly', 'Weekly'),
                   ('monthly', 'Monthly'),
                   ('suspended', 'Suspended'),
                   ('regular', 'Regular'),
                   ('blocked', 'Blocked')
                   ])
    purchase_id = fields.Many2one('purchase.order', string="RFQ Item")
    scope_ids = fields.Many2many('service.scope', string="Services")
    pol_id = fields.Many2one(comodel_name='port.cites', string='POL')
    pod_id = fields.Many2one(comodel_name='port.cites', string='POD')
    transport_type_id = fields.Many2one('transport.type', string="Transport Type")
    shipment_scope_id = fields.Many2one('shipment.scop', string="Shipment Scope",
                                        domain=[('type', '=', 'sea')])
    package_type = fields.Many2one('package.type', string="Package Type")
    container_type = fields.Many2one('container.type', string="Container Type")
    note = fields.Text('Notes')

    pol_country_name = fields.Char(string="POL Country", compute="_compute_pol_country_name", store=True)
    pod_country_name = fields.Char(string="POD Country", compute="_compute_pod_country_name", store=True)

    @api.depends('pol_id')
    def _compute_pol_country_name(self):
        for record in self:
            record.pol_country_name = record.pol_id.country_id.name if record.pol_id and record.pol_id.country_id else ''

    @api.depends('pod_id')
    def _compute_pod_country_name(self):
        for record in self:
            record.pod_country_name = record.pod_id.country_id.name if record.pod_id and record.pod_id.country_id else ''

    @api.model
    def create(self, vals):
        # Fetch the transport_type_id from product.template and autofill it in product.supplierinfo
        if 'product_tmpl_id' in vals:
            product_template = self.env['product.template'].browse(vals['product_tmpl_id'])
            vals['transport_type_id'] = product_template.transport_type_id.id
            vals['shipment_scope_id'] = product_template.shipment_scope_id.id
            vals['package_type'] = product_template.package_type.id
            vals['container_type'] = product_template.container_type.id
            vals['pol_id'] = product_template.pol_id.id
            vals['pod_id'] = product_template.pod_id.id
            vals['scope_ids'] = [(6, 0, product_template.scope_ids.ids)]
        return super(ProductSupplierInfo, self).create(vals)

    def write(self, vals):
        # Check if product_tmpl_id is in vals or already exists on the record
        product_template_id = vals.get('product_tmpl_id') or self.product_tmpl_id.id
        if product_template_id:
            product_template = self.env['product.template'].browse(product_template_id)
            vals['transport_type_id'] = product_template.transport_type_id.id
            vals['shipment_scope_id'] = product_template.shipment_scope_id.id
            vals['package_type'] = product_template.package_type.id
            vals['container_type'] = product_template.container_type.id
            vals['pol_id'] = product_template.pol_id.id
            vals['pod_id'] = product_template.pod_id.id

            # Set scope_ids if it exists in product_template
            if 'product_tmpl_id' in vals or not self.scope_ids:
                if product_template.scope_ids:
                    vals['scope_ids'] = [(6, 0, product_template.scope_ids.ids)]
                else:
                    vals['scope_ids'] = [(5,)]  # Clear the field if empty

        return super(ProductSupplierInfo, self).write(vals)

    # def write(self, vals):
    #     # Autofill transport_type_id in case the product template's transport type changes
    #     if 'product_tmpl_id' in vals:
    #         product_template_id = vals.get('product_tmpl_id') or self.product_tmpl_id.id
    #         if product_template_id:
    #             product_template = self.env['product.template'].browse(product_template_id)
    #             vals['transport_type_id'] = product_template_id.transport_type_id.id
    #             vals['shipment_scope_id'] = product_template_id.shipment_scope_id.id
    #             vals['package_type'] = product_template_id.package_type.id
    #             vals['container_type'] = product_template_id.container_type.id
    #             vals['pol_id'] = product_template_id.pol_id.id
    #             vals['pod_id'] = product_template_id.pod_id.id
    #             vals['scope_ids'] = [(6, 0, product_template_id.scope_ids.ids)]
    #     return super(ProductSupplierInfo, self).write(vals)

    count_rfqs = fields.Integer(string="Purchase", compute='get_purchase_count')
    count_pricing = fields.Integer(string="Pricing", compute='get_pricing_count')

    def action_view_rfqs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('id', '=', self.purchase_id.id), ('purchase_type', '=', 'freight')],
            'multi': False,
            'name': 'Purchase',
            'target': 'current',
            'res_model': 'purchase.order',
            'view_mode': 'tree,form',
        }

    def action_view_pricing(self):
        self.ensure_one()
        tree_view_id = self.env.ref('eit_freight_pricing.product_template_tree_view_pricing2').id
        form_view_id = self.env.ref('eit_freight_pricing.product_template_form_view_pricing2').id
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'object',
            'domain': [('id', '=', self.product_tmpl_id.id), ('detailed_type', '=', 'pricing')],
            'multi': False,
            'name': 'Pricing',
            'target': 'current',
            'res_model': 'product.template',
            'view_mode': 'tree,form',
            'views': [
                (tree_view_id, 'tree'),  # Tree view
                (form_view_id, 'form')  # Form view
            ],
            # 'view_id': self.env.ref('eit_freight_pricing.product_template_tree_view_pricing2').id,
        }

    def get_purchase_count(self):
        for rec in self:
            count = self.env['purchase.order'].search_count(
                [('id', '=', self.purchase_id.id), ('purchase_type', '=', 'freight')])
            rec.count_rfqs = count

    def get_pricing_count(self):
        for rec in self:
            count = self.env['product.template'].search_count(
                [('id', '=', self.product_tmpl_id.id), ('detailed_type', '=', 'pricing')])
            rec.count_pricing = count

    @api.onchange('purchase_id')
    def onchange_purchase_id(self):
        for rec in self:
            if rec.purchase_id:
                rec.partner_id = rec.purchase_id.partner_id.id
