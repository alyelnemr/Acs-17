# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime
from odoo.exceptions import ValidationError
from datetime import timedelta


class Project(models.Model):
    _inherit = "project.project"

    activity_type = fields.Many2one('activity.type', string="Activity Type")
    industry_id = fields.Many2one('res.partner.industry', string="Industry")
    created_by = fields.Many2one('res.users', string="Created By", default=lambda self: self.env.user)
    created_on = fields.Datetime(string="Created On", default=fields.Datetime.now)
    privacy_visibility = fields.Selection(selection_add=[
        ('invited_portal_internal', 'Invited portal users and Invited internal users (private)')
    ], ondelete={'invited_portal_internal': 'set default'})
    project_doc_lines = fields.One2many('project.document.line', 'project_id', string="Doc Lines")

    def _get_default_stages(self):
        stages = self.env['project.task.type'].search([('name', 'in', ['Open', 'Invoice', 'Closed', 'Cancelled'])])
        return stages.ids

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == _('New') or vals.get('name') == False:
            vals['name'] = self.env['res.partner'].browse(vals.get('partner_id')).name
        if not vals.get('type_ids'):
            vals['type_ids'] = [(6, 0, self._get_default_stages())]
        return super(Project, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner(self):
        for record in self:
            if record.partner_id:
                record.name = record.partner_id.name


class ProjectDocument(models.Model):
    _name = "project.document.line"
    _description = "Project Document Lines"

    project_id = fields.Many2one('project.project', string="Project")
    doc_name = fields.Many2one('document.type', string="Doc Name")
    doc_number = fields.Text(string="Doc Number")
    doc_expiry = fields.Date(string="Doc Expiry")
    doc_link = fields.Many2one('documents.document', string='Document', ondelete='restrict')

    def button_function(self):
        pass
