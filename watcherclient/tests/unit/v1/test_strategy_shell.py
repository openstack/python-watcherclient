# Copyright (c) 2016 b<>com
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

from oslo_serialization import jsonutils

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

STRATEGY_1 = {
    'uuid': '2cf86250-d309-4b81-818e-1537f3dba6e5',
    'name': 'basic',
    'display_name': 'Basic consolidation',
    'goal_uuid': 'fc087747-61be-4aad-8126-b701731ae836',
    'goal_name': 'SERVER_CONSOLIDATION',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'parameters_spec': {},
}

STRATEGY_2 = {
    'uuid': 'b20bb987-ea8f-457a-a4ea-ab3ffdfeff8b',
    'name': 'dummy',
    'display_name': 'Dummy',
    'goal_uuid': '407b03b1-63c6-49b2-adaf-4df5c0090047',
    'goal_name': 'DUMMY',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'parameters_spec': {},
}


class StrategyShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.STRATEGY_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.STRATEGY_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.STRATEGY_FIELDS
    FIELD_LABELS = resource_fields.STRATEGY_FIELD_LABELS
    STATE_FIELDS = resource_fields.STRATEGY_STATE_FIELDS
    STATE_FIELD_LABELS = resource_fields.STRATEGY_STATE_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_strategy_manager = mock.patch.object(resource, 'StrategyManager')
        self.m_strategy_mgr_cls = p_strategy_manager.start()
        self.addCleanup(p_strategy_manager.stop)

        self.m_strategy_mgr = mock.Mock()
        self.m_strategy_mgr_cls.return_value = self.m_strategy_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_strategy_list(self):
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        strategy2 = resource.Strategy(mock.Mock(), STRATEGY_2)
        self.m_strategy_mgr.list.return_value = [
            strategy1, strategy2]

        exit_code, results = self.run_cmd('strategy list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(strategy1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(strategy2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_strategy_mgr.list.assert_called_once_with(detail=False)

    def test_do_strategy_list_marker(self):
        strategy2 = resource.Strategy(mock.Mock(), STRATEGY_2)
        self.m_strategy_mgr.list.return_value = [strategy2]

        exit_code, results = self.run_cmd(
            'strategy list --marker 2cf86250-d309-4b81-818e-1537f3dba6e5')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(strategy2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_strategy_mgr.list.assert_called_once_with(
            detail=False,
            marker='2cf86250-d309-4b81-818e-1537f3dba6e5')

    def test_do_strategy_list_detail(self):
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        strategy2 = resource.Strategy(mock.Mock(), STRATEGY_2)
        self.m_strategy_mgr.list.return_value = [
            strategy1, strategy2]

        exit_code, results = self.run_cmd('strategy list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(strategy1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(strategy2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)

        self.m_strategy_mgr.list.assert_called_once_with(detail=True)

    def test_do_strategy_list_filter_by_goal_name(self):
        strategy2 = resource.Strategy(mock.Mock(), STRATEGY_2)
        self.m_strategy_mgr.list.return_value = [strategy2]

        exit_code, results = self.run_cmd(
            'strategy list --goal '
            'DUMMY')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(strategy2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_strategy_mgr.list.assert_called_once_with(
            detail=False,
            goal='DUMMY',
        )

    def test_do_strategy_list_filter_by_goal_uuid(self):
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        self.m_strategy_mgr.list.return_value = [strategy1]

        exit_code, results = self.run_cmd(
            'strategy list --goal '
            'fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(strategy1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_strategy_mgr.list.assert_called_once_with(
            detail=False,
            goal='fc087747-61be-4aad-8126-b701731ae836',
        )

    def test_do_strategy_show_by_uuid(self):
        strategy = resource.Strategy(mock.Mock(), STRATEGY_1)
        self.m_strategy_mgr.get.return_value = strategy

        exit_code, result = self.run_cmd(
            'strategy show f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(strategy, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_strategy_mgr.get.assert_called_once_with(
            'f8e47706-efcf-49a4-a5c4-af604eb492f2')

    def test_do_strategy_state(self):
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        strategy_req = [
            {'type': 'Datasource', 'mandatory': True,
             'comment': '', 'state': 'gnocchi: True'},
            {'type': 'Metrics', 'mandatory': False,
             'comment': '', 'state': jsonutils.dumps([
                 {'compute.node.cpu.percent': 'available'},
                 {'cpu_util': 'available'},
                 {'memory.resident': 'available'},
                 {'hardware.memory.used': 'not available'}])},
            {'type': 'CDM', 'mandatory': True,
             'comment': '',
             'state': jsonutils.dumps([{'compute_model': 'available'},
                                      {'storage_model': 'not available'}])},
            {'type': 'Name', 'mandatory': '', 'comment': '',
             'state': strategy1.name}]
        requirements = [resource.Strategy(mock.Mock(), req)
                        for req in strategy_req]
        self.m_strategy_mgr.state.return_value = requirements

        exit_code, results = self.run_cmd('strategy state basic')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(req, self.STATE_FIELDS,
                                   self.STATE_FIELD_LABELS)
             for req in requirements],
            results)
