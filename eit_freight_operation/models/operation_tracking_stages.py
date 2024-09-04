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
    tracking_stage_domain = fields.Char(string="Tracking Stage Domain", compute='_compute_tracking_stage_domain')

    @api.onchange('tracking_type')
    def _compute_tracking_stage_domain(self):
        for record in self:
            if record.tracking_type == 'clearance':
                record.tracking_stage_domain = "[('stage_clearance', '=', True)]"
            elif record.tracking_type == 'freight':
                record.tracking_stage_domain = "[('stage_freight', '=', True), ('stage_clearance', '=', False)]"
            else:
                record.tracking_stage_domain = "[]"
    #
    # @api.onchange('tracking_type')
    # def _onchange_tracking_type(self):
    #     stage_clearance = self.tracking_type == 'clearance'
    #     stage_freight = self.tracking_type == 'freight'
    #     if stage_clearance:
    #         return {
    #             'domain': {
    #                 'tracking_stage': [('stage_clearance', '=', True)]
    #             }
    #         }
    #     elif stage_freight:
    #         return {
    #             'domain': {
    #                 'tracking_stage': [('stage_freight', '=', True), ('stage_clearance', '=', False)]
    #             }
    #         }
    #     else:
    #         return {
    #             'domain': {
    #                 'tracking_stage': []
    #             }
    #         }
