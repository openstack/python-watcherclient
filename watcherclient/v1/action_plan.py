#
# Copyright 2013 Red Hat, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from watcherclient.common import base
from watcherclient.common import utils
# from watcherclient import exceptions as exc


class ActionPlan(base.Resource):
    def __repr__(self):
        return "<ActionPlan %s>" % self._info


class ActionPlanManager(base.Manager):
    resource_class = ActionPlan

    @staticmethod
    def _path(id=None, q_param=None):
        if id and q_param:
            return '/v1/action_plans/%s/%s' % (id, q_param)
        elif id:
            return '/v1/action_plans/%s' % id
        else:
            return '/v1/action_plans'

    def list(self, audit=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, marker=None):
        """Retrieve a list of action plan.

        :param audit: Name of the audit
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of action plans to return.
            2) limit == 0, return the entire list of action plans.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about action plans.

        :param marker: The last actionplan UUID of the previous page;
                       displays list of actionplans after "marker".

        :returns: A list of action plans.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)
        if audit is not None:
            filters.append('audit_uuid=%s' % audit)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "action_plans")
        else:
            return self._list_pagination(self._path(path), "action_plans",
                                         limit=limit)

    def get(self, action_plan_id):
        try:
            return self._list(self._path(action_plan_id))[0]
        except IndexError:
            return None

    def delete(self, action_plan_id):
        return self._delete(self._path(action_plan_id))

    def update(self, action_plan_id, patch):
        return self._update(self._path(action_plan_id), patch)

    def start(self, action_plan_id):
        return self._start(self._path(action_plan_id, 'start'))

    def cancel(self, action_plan_id):
        action_plan = self.get(action_plan_id)
        if action_plan.state == "ONGOING":
            patch = [{'op': 'replace', 'value': 'CANCELLING',
                      'path': '/state'}]
        else:
            patch = [{'op': 'replace', 'value': 'CANCELLED', 'path': '/state'}]
        return self._update(self._path(action_plan_id), patch)
