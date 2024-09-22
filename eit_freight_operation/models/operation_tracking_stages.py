from datetime import timedelta

from odoo import models, fields, api


class OperationTrackingStages(models.Model):
    _name = 'operation.tracking.stages'
    _description = 'Tracking stages'
    _order = 'expected_date desc, create_date desc'

    tracking_type = fields.Selection([('freight', 'Freight'), ('clearance', 'Clearance')], string="Tracking Type",
                                     required=True, default='freight')
    description = fields.Text(string="Stage Description")
    tracking_stage = fields.Many2one(comodel_name='tracking.stage', string="Tracking Stage", required=True)
    is_done = fields.Boolean(string="Is Done", default=True)
    tracking_date = fields.Date(string="Tracking Date", default=fields.Date.today())
    project_task_id = fields.Many2one(comodel_name='project.task', string='Project Task')
    next_tracking_stage = fields.Many2one(comodel_name='tracking.stage', string="Next Tracking Stage", required=True)
    expected_date = fields.Date(string="Tracking Date", default=lambda self: fields.Date.today() + timedelta(days=7))
    next_description = fields.Text(string="Next Stage Description")
    clearence_type_id = fields.Many2one('clearence.type', string="Direction",
                                        related='project_task_id.clearence_type_id')
    tracking_stage_domain = fields.Char(string="Tracking Stage Domain", compute='_compute_tracking_stage_domain')

    @api.onchange('tracking_stage')
    def onchange_tracking_stage(self):
        for record in self:
            if record.tracking_stage:
                record.description = record.tracking_stage.description

    @api.onchange('next_tracking_stage')
    def onchange_next_tracking_stage(self):
        for record in self:
            if record.next_tracking_stage:
                record.next_description = record.next_tracking_stage.description
