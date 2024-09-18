# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import email_normalize


class ResPartner(models.Model):
    """ Inherits partner and adds Tasks information in the partner form """
    _inherit = 'res.partner'

    task_count = fields.Integer(compute='_compute_task_count', string='# Shipments')

    def _compute_task_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search_fetch(
            [('id', 'child_of', self.ids)],
            ['parent_id'],
        )
        all_opt_partners = self.env['opt.partners'].search([('partner_id', 'in', all_partners.ids)]).mapped('task_id')

        task_data = self.env['project.task']._read_group(
            domain=[('partner_id', 'in', self.ids)],
            groupby=['partner_id'], aggregates=['__count']
        )

        self_ids = set(self._ids)

        self.task_count = 0
        for partner, count in task_data:
            while partner:
                if partner.id in self_ids:
                    partner.task_count += count
                    partner.task_count += len(all_opt_partners)
                partner = partner.parent_id

    def action_view_tasks(self):
        """ Open the related tasks for this partner """
        self.ensure_one()

        # Retrieve all tasks linked to this partner
        task_ids = self.env['project.task'].search([('partner_id', 'in', self.ids)]).ids

        # Retrieve tasks related to this partner via opt.partners
        opt_task_ids = self.env['opt.partners'].search([('partner_id', 'in', self.ids)]).mapped('task_id').ids

        # Combine all task IDs
        all_task_ids = list(set(task_ids + opt_task_ids))

        # Return action to display these tasks
        return {
            'type': 'ir.actions.act_window',
            'name': 'Shipments',
            'res_model': 'project.task',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', all_task_ids)],
        }
