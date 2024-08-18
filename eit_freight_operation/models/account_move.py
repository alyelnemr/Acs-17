from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_freight = fields.Boolean(string="Freight", default=False)
    transport_type_id = fields.Many2one(comodel_name='transport.type', string="Transport Type")
    master_bl = fields.Text(string="Master B/L")
    pol = fields.Many2one(comodel_name='port.cites', string="POL(Info)")
    pod = fields.Many2one(comodel_name='port.cites', string="POD(Info)")
    show_packages = fields.Boolean(string="Show Packages", default=False)
    show_containers = fields.Boolean(string="Show Containers", default=False)
    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")
    invoice_nature = fields.Selection(selection=[('taxable', 'Taxable'), ('nontaxable', 'Nontaxable')],
                                      string="Invoice Nature")
    active = fields.Boolean(string="Active", default=True)

    def action_open_project_task(self):
        self.ensure_one()
        if self.project_task_id:
            return {
                'type': 'ir.actions.act_window',
                'name': 'Project Task',
                'view_mode': 'form',
                'res_model': 'project.task',
                'res_id': self.project_task_id.id,
                'target': 'current',
            }
        else:
            return False

    def button_draft(self):
        res = super().button_draft()
        if self.is_freight:
            error = False
            if len(self.line_ids.filtered(
                    lambda x: x.invoice_project_task_charge_id or x.vendor_bill_project_task_charge_id)) == 0:
                error = True
            for line in self.line_ids.filtered(
                    lambda x: x.invoice_project_task_charge_id or x.vendor_bill_project_task_charge_id):
                project_task_check = self.env['project.task.charges'].search(
                    ['|', ('invoice_id', '=', self.id), ('vendor_bill_id', '=', self.id)], limit=1)
                if not project_task_check:
                    error = True
            if error:
                raise ValidationError(
                    "You cannot reset to draft because there are no project tasks valid for this invoice/bill.")

        return res

    def button_draft(self):
        res = super().button_draft()
        self.active = False
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    package_type_id = fields.Many2one(comodel_name='package.type', string="Package")
    container_type_id = fields.Many2one(comodel_name='container.type', string="Container")
    invoice_project_task_charge_id = fields.Many2one(comodel_name='project.task.charges', string="Project Task Charges")
    vendor_bill_project_task_charge_id = fields.Many2one(comodel_name='project.task.charges',
                                                         string="Vendor Bill Charges")

    @api.onchange('move_id.move_type', 'product_id', 'move_id.name', 'move_id.partner_id')
    def _onchange_move_id(self):
        if self.move_id.move_type == 'out_invoice' and self.move_id.is_freight:
            return {'domain': {'product_id': [('detailed_type', '=', 'charge_type')]}}
        elif self.move_id.is_freight:
            return {'domain': {'product_id': [('detailed_type', 'in', ('consu', 'service', 'charge_type'))]}}

    def unlink(self):
        for line in self:
            if line.invoice_project_task_charge_id or line.vendor_bill_project_task_charge_id:
                raise UserError("You cannot delete this record because it is linked to a project task charge.")
        return super(AccountMoveLine, self).unlink()
