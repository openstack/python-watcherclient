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

import six.moves.urllib.parse as parse

from watcherclient.common import base
from watcherclient.common import utils


class Strategy(base.Resource):
    def __repr__(self):
        return "<Strategy %s>" % self._info


class StrategyManager(base.Manager):
    resource_class = Strategy

    @staticmethod
    def _path(strategy=None, state=False):
        if strategy:
            path = '/v1/strategies/%s' % strategy
            if state:
                path = '/v1/strategies/%s/state' % strategy
        else:
            path = '/v1/strategies'
        return path

    def list(self, goal=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, marker=None):
        """Retrieve a list of strategy.

        :param goal: The UUID of the goal to filter by
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
        :param marker: Optional, UUID of the last strategy in the previous
                       page.
        :returns: A list of audits.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)

        if goal:
            filters.append(parse.urlencode(dict(goal=goal)))

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "strategies")
        else:
            return self._list_pagination(self._path(path), "strategies",
                                         limit=limit)

    def get(self, strategy):
        try:
            return self._list(self._path(strategy))[0]
        except IndexError:
            return None

    def state(self, strategy):
        return self._list(self._path(strategy, state=True))
