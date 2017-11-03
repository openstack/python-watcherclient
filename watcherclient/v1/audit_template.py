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

CREATION_ATTRIBUTES = ['description', 'name', 'goal', 'strategy', 'scope']


class AuditTemplate(base.Resource):
    def __repr__(self):
        return "<AuditTemplate %s>" % self._info


class AuditTemplateManager(base.Manager):
    resource_class = AuditTemplate

    @staticmethod
    def _path(id_=None):
        return '/v1/audit_templates/%s' % id_ if id_ else '/v1/audit_templates'

    def list(self, name=None, goal=None, strategy=None, limit=None,
             sort_key=None, sort_dir=None, detail=False, marker=None):
        """Retrieve a list of audit template.

        :param name: Name of the audit template
        :param limit: The maximum number of results to return per
                      request, if:

            1) limit > 0, the maximum number of audit templates to return.
            2) limit == 0, return the entire list of audit_templates.
            3) limit param is NOT specified (None), the number of items
               returned respect the maximum imposed by the Watcher API
               (see Watcher's api.max_limit option).

        :param sort_key: Optional, field used for sorting.

        :param sort_dir: Optional, direction of sorting, either 'asc' (the
                         default) or 'desc'.

        :param detail: Optional, boolean whether to return detailed information
                       about audit_templates.

        :param marker: Optional, UUID of the last audit template of
                       the previous page.

        :returns: A list of audit templates.

        """
        if limit is not None:
            limit = int(limit)

        filters = utils.common_filters(limit, sort_key, sort_dir, marker)
        if name is not None:
            filters.append('name=%s' % name)
        if goal is not None:
            filters.append("goal=%s" % goal)
        if strategy is not None:
            filters.append("strategy=%s" % strategy)

        path = ''
        if detail:
            path += 'detail'
        if filters:
            path += '?' + '&'.join(filters)

        if limit is None:
            return self._list(self._path(path), "audit_templates")
        else:
            return self._list_pagination(self._path(path), "audit_templates",
                                         limit=limit)

    def get(self, audit_template_id):
        try:
            return self._list(self._path(audit_template_id))[0]
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

    def delete(self, audit_template_id):
        return self._delete(self._path(audit_template_id))

    def update(self, audit_template_id, patch):
        return self._update(self._path(audit_template_id), patch)
