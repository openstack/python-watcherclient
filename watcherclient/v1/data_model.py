# Copyright 2019 ZTE Corporation.
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


class DataModel(base.Resource):
    def __repr__(self):
        return "<DataModel %s>" % self._info


class DataModelManager(base.Manager):
    resource_class = DataModel

    @staticmethod
    def _path(filters=None):
        if filters:
            path = '/v1/data_model/%s' % filters
        else:
            path = '/v1/data_model'
        return path

    def list(self, data_model_type='compute', audit=None):
        """Retrieve a list of data model.

        :param data_model_type: The type of data model user wants to list.
                                Supported values: compute.
                                Future support values: storage, baremetal.
                                The default value is compute.
        :param audit: The UUID of the audit, used to filter data model
                      by the scope in audit.

        :returns: A list of data model.

        """
        path = ''
        filters = utils.common_filters()

        if audit:
            filters.append('audit_uuid=%s' % audit)
        filters.append('data_model_type=%s' % data_model_type)

        path += '?' + '&'.join(filters)

        return self._list(self._path(path))[0]
