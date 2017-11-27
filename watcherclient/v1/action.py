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


class Action(base.Resource):
    def __repr__(self):
        return "<Action %s>" % self._info


class ActionManager(base.Manager):
    resource_class = Action

    @staticmethod
    def _path(id=None):
        return '/v1/actions/%s' % id if id else '/v1/actions'

    def list(self, action_plan=None, audit=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, marker=None):
        """Retrieve a list of action.

        :param action_plan: UUID of the action plan
        :param audit: UUID of the audit
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of actions to return.
            2) limit == 0, return the entire list of actions.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about actions.

        :param marker: Optional, UUID of the last action in the previous page.

        :returns: A list of actions.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)
        if action_plan is not None:
            filters.append('action_plan_uuid=%s' % action_plan)
        if audit is not None:
            filters.append('audit_uuid=%s' % audit)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "actions")
        else:
            return self._list_pagination(self._path(path), "actions",
                                         limit=limit)

    def get(self, action_id):
        try:
            return self._list(self._path(action_id))[0]
        except IndexError:
            return None
