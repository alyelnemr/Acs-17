from odoo import models, fields, api


class ProjectTaskCreateInvoiceWizard(models.TransientModel):
    _name = 'project.task.charge.invoice.partner.wizard'
    _description = 'Wizard to Create Invoice from Project Task'

    def default_get(self, fields_list):
        res = super(ProjectTaskCreateInvoiceWizard, self).default_get(fields_list)

        # Get the active ID from the context, which should be the project.task ID
        active_id = self.env.context.get('active_id')
        if active_id and 'project_task_id' in fields_list:
            task = self.env['project.task'].browse(active_id)
            previous_wizard = self.env['project.task.charge.partners.wizard'].search(
                [('project_task_id', '=', task.id)])
            previous_wizard.unlink()
            if task:
                # Populate the wizard with opt_partners from the task
                opt_partner_wizard_data = []
                for partner_line in task.opt_partners_lines:
                    # Create the selection option as a concatenation of partner_type and partner_id.name
                    option_label = f"({partner_line.partner_type_id.name}) {partner_line.partner_id.name}"
                    opt_partner_wizard_data.append({
                        'partner_type_partner': option_label,
                        'partner_type_partner_id': partner_line.partner_id.id,
                        'project_task_id': task.id,
                    })

                if opt_partner_wizard_data:
                    self.env['project.task.charge.partners.wizard'].create(opt_partner_wizard_data)

                res.update({
                    'project_task_id': task.id,
                })
        return res

    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")
    invoice_or_vendor_bill = fields.Selection(selection=[('invoice', 'Invoice'), ('vendor_bill', 'Vendor Bill')],
                                              default='invoice')
    opt_partner_wizard_ids = fields.Many2one(comodel_name='project.task.charge.partners.wizard', string="Partner",
                                             domain="[('project_task_id', '=', project_task_id)]",
                                             ondelete='set null')

    def action_create_invoice(self):
        self.ensure_one()
        error_message = ''
        partner = self.opt_partner_wizard_ids.partner_type_partner_id
        if self.invoice_or_vendor_bill == 'invoice':
            error_message = self.project_task_id.action_create_customer_invoice(partner_id=partner)
        if self.invoice_or_vendor_bill == 'vendor_bill':
            error_message = self.project_task_id.action_create_vendor_bill(partner_id=partner)
        if error_message:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': "Operation Failed",
                    'message': error_message,
                    'type': 'warning',
                    'sticky': False,
                },
            }
        return {'type': 'ir.actions.act_window_close'}


class OptPartnersWizard(models.TransientModel):
    _name = "project.task.charge.partners.wizard"
    _description = "Opt partners"
    _rec_name = "partner_type_partner"
    _order = 'partner_type_partner'

    project_task_id = fields.Many2one(comodel_name='project.task', string="Project Task")
    partner_type_partner = fields.Char(string="Partner")
    partner_type_partner_id = fields.Integer(string="Partner")
