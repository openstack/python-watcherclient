# -*- coding: utf-8 -*-
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
from watcherclient import exceptions as exc

CREATION_ATTRIBUTES = ['endpoint', 'category']


class MetricCollector(base.Resource):
    def __repr__(self):
        return "<MetricCollector %s>" % self._info


class MetricCollectorManager(base.Manager):
    resource_class = MetricCollector

    @staticmethod
    def _path(id=None):
        return \
            '/v1/metric-collectors/%s' % id if id else '/v1/metric-collectors'

    def list(self, category=None, limit=None, sort_key=None,
             sort_dir=None, detail=False):
        """Retrieve a list of metric collector.

        :param category: Optional, Metric category, to get all metric
                         collectors mapped with this category.
        :param limit: The maximum number of results to return per
                  request, if:

            1) limit > 0, the maximum number of metric collectors to return.
            2) limit == 0, return the entire list of metriccollectors.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about metric collectors.

        :returns: A list of metric collectors.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir)
        if category is not None:
            filters.append('category=%s' % category)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "metric-collectors")
        else:
            return self._list_pagination(self._path(path), "metric-collectors",
                                         limit=limit)

    def get(self, metric_collector_id):
        try:
            return self._list(self._path(metric_collector_id))[0]
        except IndexError:
            return None

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exc.InvalidAttribute()
        return self._create(self._path(), new)

    def delete(self, metric_collector_id):
        return self._delete(self._path(metric_collector_id))

    def update(self, metric_collector_id, patch):
        return self._update(self._path(metric_collector_id), patch)
