#
# Copyright 2016 Intel
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


class ScoringEngine(base.Resource):
    def __repr__(self):
        return "<ScoringEngine %s>" % self._info


class ScoringEngineManager(base.Manager):
    resource_class = ScoringEngine

    @staticmethod
    def _path(scoring_engine=None):
        return ('/v1/scoring_engines/%s' % scoring_engine
                if scoring_engine else '/v1/scoring_engines')

    def list(self, limit=None, sort_key=None, sort_dir=None, detail=False):
        """Retrieve a list of scoring engines.

        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of scoring engines to return.
            2) limit == 0, return the entire list of scoring engines.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about scoring engines.

        :returns: A list of scoring engines.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "scoring_engines")
        else:
            return self._list_pagination(self._path(path), "scoring_engines",
                                         limit=limit)

    def get(self, scoring_engine_name):
        try:
            return self._list(self._path(scoring_engine_name))[0]
        except IndexError:
            return None
