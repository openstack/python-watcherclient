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


CREATION_ATTRIBUTES = ['audit_template_uuid', 'audit_type', 'interval',
                       'parameters', 'goal', 'strategy', 'auto_trigger',
                       'name', 'start_time', 'end_time', 'force']


class Audit(base.Resource):
    def __repr__(self):
        return "<Audit %s>" % self._info


class AuditManager(base.Manager):
    resource_class = Audit

    @staticmethod
    def _path(id=None):
        return '/v1/audits/%s' % id if id else '/v1/audits'

    def list(self, audit_template=None, limit=None, sort_key=None,
             sort_dir=None, detail=False, goal=None, strategy=None,
             marker=None):
        """Retrieve a list of audit.

        :param audit_template: Name of the audit template
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

        :param marker: Optional, UUID of the last audit in the previous page.

        :returns: A list of audits.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)
        if audit_template is not None:
            filters.append('audit_template=%s' % audit_template)
        if goal is not None:
            filters.append('goal=%s' % goal)
        if strategy is not None:
            filters.append('strategy=%s' % strategy)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "audits")
        else:
            return self._list_pagination(self._path(path), "audits",
                                         limit=limit)

    def create(self, **kwargs):
        new = {}
        for (key, value) in kwargs.items():
            if key in CREATION_ATTRIBUTES:
                new[key] = value
            else:
                raise exc.InvalidAttribute()
        return self._create(self._path(), new)

    def get(self, audit):
        try:
            return self._list(self._path(audit))[0]
        except IndexError:
            return None

    def delete(self, audit):
        return self._delete(self._path(audit))

    def update(self, audit, patch):
        return self._update(self._path(audit), patch)
