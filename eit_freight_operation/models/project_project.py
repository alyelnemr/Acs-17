# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, _lt
from odoo.addons.rating.models import rating_data
import json
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
        ('portal_followers', 'Invited portal users (public) and Invited internal users (private)')
    ], ondelete={'portal_followers': 'set default'},
        default='portal_followers')
    project_doc_lines = fields.One2many('project.document.line', 'project_id', string="Doc Lines")

    def _get_default_stages(self):
        stages = self.env['project.task.type'].search([('is_default', '=', True)])
        return stages.ids

    def replace_tasks_with_operations(self, data):
        for entry in data:
            if str(entry['text']) == 'Tasks':
                entry['text'] = _lt('Operations')
            elif str(entry['text']) == 'Sales Orders':
                entry['text'] = _lt('Bookings')
            elif str(entry['text']) == 'Sales Order Items':
                entry['text'] = _lt('Bookings Items')

    def _get_stat_buttons(self):
        buttons = super(Project, self)._get_stat_buttons()
        self.replace_tasks_with_operations(buttons)
        return buttons

    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('name') == _('New') or not vals.get('name'):
            vals['name'] = self.env['res.partner'].browse(vals.get('partner_id')).name
        if not vals.get('type_ids'):
            vals['type_ids'] = [(6, 0, self._get_default_stages())]
        return super(Project, self).create(vals)

    @api.onchange('partner_id')
    def onchange_partner(self):
        for record in self:
            if record.partner_id:
                record.name = record.partner_id.name

    @api.depends('privacy_visibility')
    def _compute_privacy_visibility_warning(self):
        for project in self:
            if not project.ids:
                project.privacy_visibility_warning = ''
            elif project.privacy_visibility == 'portal' and project._origin.privacy_visibility != 'portal':
                project.privacy_visibility_warning = _(
                    'Customers will be added to the followers of their project and tasks.')
            elif project.privacy_visibility not in (
            'portal', 'portal_followers') and project._origin.privacy_visibility in ('portal', 'portal_followers'):
                project.privacy_visibility_warning = _(
                    'Portal users will be removed from the followers of the project and its tasks.')
            else:
                project.privacy_visibility_warning = ''

    @api.depends('privacy_visibility')
    def _compute_access_instruction_message(self):
        for project in self:
            if project.privacy_visibility == 'portal':
                project.access_instruction_message = _(
                    'Granting Access to Operations for Employees and Portal Users.')
            elif project.privacy_visibility == 'followers':
                project.access_instruction_message = _(
                    'Grant employees access to your project or tasks by adding them as followers. Employees automatically get access to the tasks they are assigned to.')
            elif project.privacy_visibility == 'portal_followers':
                project.access_instruction_message = _(
                    """Granting Access to Operations for Employees and Portal Users. \nEmployees:\n
                    Add employees as followers to the Operations to grant them access.\n
                    Employees will automatically gain access to any tasks they are assigned to.\n
                    Portal Users:\n
                    Add portal users as followers to the Operations to grant them access.\n
                    Customers will automatically gain access to their tasks in their portal"""
                )
            else:
                project.access_instruction_message = ''

    @api.depends('collaborator_ids', 'privacy_visibility')
    def _compute_collaborator_count(self):
        project_sharings = self.filtered(lambda project: project.privacy_visibility == 'portal')
        collaborator_read_group = self.env['project.collaborator']._read_group(
            [('project_id', 'in', project_sharings.ids)],
            ['project_id'],
            ['__count'],
        )
        collaborator_count_by_project = {project.id: count for project, count in collaborator_read_group}
        for project in self:
            project.collaborator_count = collaborator_count_by_project.get(project.id, 0)

    def _change_privacy_visibility(self, new_visibility):
        """
        Unsubscribe non-internal users from the project and tasks if the project privacy visibility
        goes from 'portal' to a different value.
        If the privacy visibility is set to 'portal', subscribe back project and tasks partners.
        """
        for project in self:
            if project.privacy_visibility == new_visibility:
                continue
            if new_visibility == 'portal' or new_visibility == 'portal_followers':
                project.message_subscribe(partner_ids=project.partner_id.ids)
                for task in project.task_ids.filtered('partner_id'):
                    task.message_subscribe(partner_ids=task.partner_id.ids)
            elif project.privacy_visibility == 'portal' or project.privacy_visibility == 'portal_followers':
                portal_users = project.message_partner_ids.user_ids.filtered('share')
                project.message_unsubscribe(partner_ids=portal_users.partner_id.ids)
                project.tasks._unsubscribe_portal_users()

    # ---------------------------------------------------
    # Project sharing
    # ---------------------------------------------------
    def _check_project_sharing_access(self):
        self.ensure_one()
        if self.privacy_visibility not in ('portal_followers', 'portal'):
            return False
        if self.env.user.has_group('base.group_portal'):
            return self.env['project.collaborator'].search(
                [('project_id', '=', self.sudo().id), ('partner_id', '=', self.env.user.partner_id.id)])
        return self.env.user._is_internal()

    def _compute_access_warning(self):
        super(Project, self)._compute_access_warning()
        for project in self.filtered(lambda x: x.privacy_visibility not in ('portal', 'portal_followers')):
            project.access_warning = _(
                "The project cannot be shared with the recipient(s) because the privacy of the project is too restricted. Set the privacy to 'Visible by following customers' in order to make it accessible by the recipient(s).")


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
