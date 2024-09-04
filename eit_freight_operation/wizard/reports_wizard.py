from odoo import models, fields, api


class OperationReportsWizard(models.TransientModel):
    _name = 'operation.reports.wizard'
    _description = 'Operation Reports Wizard'

    @api.model
    def default_get(self, fields):
        res = super(OperationReportsWizard, self).default_get(fields)
        # Default task_id from context
        if 'default_task_id' in self.env.context:
            res['task_id'] = self.env.context.get('default_task_id')
        return res

    task_id = fields.Many2one('project.task', string="Task", required=True)
    report_name = fields.Selection(selection=[('operation_statement', 'Operation Statement')], string="Report Name", required=True, default='operation_statement')

    def print_report(self):
        # Method to print the report
        return self.env.ref('eit_freight_operation.report_project_task_charges_op_statement').report_action(self.task_id)
