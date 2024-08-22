# Part of Odoo. See LICENSE file for full copyright and licensing details.

import json

from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem

from odoo.osv.expression import OR, AND

from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class MyProjectCustomerPortal(ProjectCustomerPortal):

    def _task_get_searchbar_groupby(self, milestones_allowed, project=False):
        values = super()._task_get_searchbar_groupby(milestones_allowed, project)
        del values['customer']
        del values['sale_line']
        values['project']['label'] = 'Profile'
        values['sale_order']['label'] = 'Booking'
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _task_get_searchbar_sortings(self, milestones_allowed, project=False):
        values = {
            'date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'name': {'label': _('Title'), 'order': 'name', 'sequence': 2},
            'stage': {'label': _('Stage'), 'order': 'stage_id, project_id', 'sequence': 5},
            'status': {'label': _('Status'), 'order': 'state', 'sequence': 6},
            'priority': {'label': _('Priority'), 'order': 'priority desc', 'sequence': 8},
            'update': {'label': _('Last Stage Update'), 'order': 'date_last_stage_update desc', 'sequence': 11},
        }
        if not project:
            values['project'] = {'label': _('Profile'), 'order': 'project_id, stage_id', 'sequence': 3}
        if milestones_allowed:
            values['milestone'] = {'label': _('Milestone'), 'order': 'milestone_id', 'sequence': 7}
        return values
