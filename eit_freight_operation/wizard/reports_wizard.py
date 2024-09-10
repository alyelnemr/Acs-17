from odoo import models, fields, api
from odoo.exceptions import UserError


class OperationReportsWizard(models.TransientModel):
    _name = 'operation.reports.wizard'
    _description = 'Operation Reports Wizard'

    @api.model
    def default_get(self, fields):
        res = super(OperationReportsWizard, self).default_get(fields)
        # Default task_id from context
        if 'default_task_id' in self.env.context:
            res['task_id'] = self.env.context.get('default_task_id')
            res['show_invoice'] = False
        if 'default_account_move_id' in self.env.context:
            res['account_move_id'] = self.env.context.get('default_account_move_id')
            res['show_invoice'] = True
        return res

    task_id = fields.Many2one('project.task', string="Task", required=False)
    account_move_id = fields.Many2one('account.move', string="Account Move", required=False)
    task_report_name = fields.Selection(
        selection=[('operation_statement', 'Operation Statement')],
        string="Report Name", required=True, default='operation_statement')
    invoice_report_name = fields.Selection(
        selection=[('statement', 'Statement'),
                   ('invoice', 'Invoice')],
        string="Report Name", required=True, default='statement')
    show_invoice = fields.Boolean(string="Show Invoice", default=False)

    def print_report(self):
        if self.task_id and self.task_report_name == 'operation_statement':
            return self.env.ref('eit_freight_operation.report_project_task_charges_op_statement').report_action(
                self.task_id)
        if self.account_move_id:
            if self.invoice_report_name == 'statement':
                return self.env.ref('eit_freight_operation.report_project_task_charges_statement').report_action(self.account_move_id)
            if self.invoice_report_name == 'invoice':
                return self.env.ref('eit_freight_operation.report_project_task_charges_invoice').report_action(self.account_move_id)
        raise UserError('No report found')
