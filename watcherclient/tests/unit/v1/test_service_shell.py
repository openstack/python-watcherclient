# Copyright (c) 2016 Servionica
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import mock
import six

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

SERVICE_1 = {
    'name': 'watcher-applier',
    'host': 'controller',
    'status': 'ACTIVE',
    'last_seen_up': None,
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

SERVICE_2 = {
    'name': 'watcher-decision-engine',
    'host': 'controller',
    'status': 'FAILED',
    'last_seen_up': None,
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}


class ServiceShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.SERVICE_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.SERVICE_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.SERVICE_FIELDS
    FIELD_LABELS = resource_fields.SERVICE_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_service_manager = mock.patch.object(resource, 'ServiceManager')
        self.m_service_mgr_cls = p_service_manager.start()
        self.addCleanup(p_service_manager.stop)

        self.m_service_mgr = mock.Mock()
        self.m_service_mgr_cls.return_value = self.m_service_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_service_list(self):
        service1 = resource.Service(mock.Mock(), SERVICE_1)
        service2 = resource.Service(mock.Mock(), SERVICE_2)
        self.m_service_mgr.list.return_value = [
            service1, service2]

        exit_code, results = self.run_cmd('service list')

        for res in results:
            del res['ID']

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(service1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(service2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_service_mgr.list.assert_called_once_with(detail=False)

    def test_do_service_list_detail(self):
        service1 = resource.Service(mock.Mock(), SERVICE_1)
        service2 = resource.Service(mock.Mock(), SERVICE_2)
        self.m_service_mgr.list.return_value = [
            service1, service2]

        exit_code, results = self.run_cmd('service list --detail')

        for res in results:
            del res['ID']

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(service1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(service2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)

        self.m_service_mgr.list.assert_called_once_with(detail=True)

    def test_do_service_show_by_name(self):
        service = resource.Service(mock.Mock(), SERVICE_1)
        self.m_service_mgr.get.return_value = service

        exit_code, result = self.run_cmd('service show watcher-applier')

        del result['ID']

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(service, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_service_mgr.get.assert_called_once_with('watcher-applier')
