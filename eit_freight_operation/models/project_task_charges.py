from odoo import fields, models, api
from odoo.exceptions import UserError


class ProjectTaskCharges(models.Model):
    _name = 'project.task.charges'
    _description = "Project Task Charges"

    is_selected = fields.Boolean(string="Select", default=False)
    product_id = fields.Many2one(comodel_name='product.product', string="Charge Type",
                                 domain="[('detailed_type', '=', 'charge_type')]")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")
    sale_price = fields.Monetary(string="Sale price")
    cost_price = fields.Monetary(string="Cost price")
    qty = fields.Float(string="QTY", default=1)
    package_type_id = fields.Many2one('package.type', string="Package")
    container_type_id = fields.Many2one('container.type', string="Container")
    currency_id = fields.Many2one('res.currency', string="Currency")
    ex_rate = fields.Float(related='currency_id.rate', string="EX.Rate", store=True)
    sale_main_curr = fields.Float(string="Sale Main Curr", compute='_compute_tot_price')
    sale_usd = fields.Float(string="Sales(USD)",
                            compute='_compute_tot_price')
    cost_main_curr = fields.Float(string="Cost Main Curr", compute='_compute_tot_price')
    cost_usd = fields.Float(string="Cost (USD)",
                            compute='_compute_tot_price')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    invoice_id = fields.Many2one('account.move.line', string="Invoice Line")
    vendor_bill_id = fields.Many2one('account.move.line', string="Bill Line")

    def unlink(self):
        for record in self:
            if record.invoice_id or record.vendor_bill_id:
                raise UserError("You cannot delete this record because it is linked to an Invoice or a Vendor Bill.")
        return super(ProjectTaskCharges, self).unlink()

    @api.depends('sale_price', 'ex_rate', 'qty', 'cost_price')
    def _compute_tot_price(self):
        for record in self:
            inverse_company_rate = 1.0
            if record.sale_price and record.ex_rate:
                record.sale_main_curr = record.sale_price * record.ex_rate
            else:
                record.sale_main_curr = 0

            if record.ex_rate:
                currency_id = self.env['res.currency'].search([('name', '=', 'USD')])
                if currency_id:
                    inverse_company_rate = currency_id.rate_ids[0].inverse_company_rate if currency_id.rate_ids else 1.0

                record.cost_main_curr = record.cost_price * record.ex_rate
                record.cost_usd = inverse_company_rate * record.cost_main_curr
                record.sale_usd = inverse_company_rate * record.sale_main_curr
            else:
                record.cost_main_curr = 0
                record.cost_usd = 0
                record.sale_usd = 0


class TotalCostCurrency(models.Model):
    _name = 'total.cost.line'
    _description = "Total cost Lines for Project Task"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")


class TotalSaleCurrency(models.Model):
    _name = 'total.sale.line'
    _description = "Total sale Lines for Project Task"

    currency_id = fields.Many2one('res.currency', string="Currency")
    amount = fields.Float(string="Amount")
    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")
