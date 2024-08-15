from odoo import models, fields, api


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


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    package_type_id = fields.Many2one(comodel_name='package.type', string="Package")
    container_type_id = fields.Many2one(comodel_name='container.type', string="Container")

    @api.onchange('move_id.move_type', 'product_id', 'move_id.name', 'move_id.partner_id')
    def _onchange_move_id(self):
        if self.move_id.move_type == 'out_invoice' and self.move_id.is_freight:
            return {'domain': {'product_id': [('detailed_type', '=', 'charge_type')]}}
        elif self.move_id.is_freight:
            return {'domain': {'product_id': [('detailed_type', 'in', ('consu', 'service', 'charge_type'))]}}
