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


class Goal(base.Resource):
    def __repr__(self):
        return "<Goal %s>" % self._info


class GoalManager(base.Manager):
    resource_class = Goal

    @staticmethod
    def _path(goal=None):
        return '/v1/goals/%s' % goal if goal else '/v1/goals'

    def list(self, limit=None, sort_key=None, sort_dir=None, detail=False,
             marker=None):
        """Retrieve a list of goal.

        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of audits to return.
            2) limit == 0, return the entire list of audits.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about audits.

        :param marker: Optional, UUID of the last goal in the previous page.

        :returns: A list of goals.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)
        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "goals")
        else:
            return self._list_pagination(self._path(path), "goals",
                                         limit=limit)

    def get(self, goal):
        try:
            return self._list(self._path(goal))[0]
        except IndexError:
            return None
