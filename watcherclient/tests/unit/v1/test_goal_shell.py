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

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

GOAL_1 = {
    'uuid': "fc087747-61be-4aad-8126-b701731ae836",
    'name': "SERVER_CONSOLIDATION",
    'display_name': 'Server Consolidation',
    'efficacy_specification': [
        {'description': 'Indicator 1', 'name': 'indicator1',
         'schema': 'Range(min=0, max=100, min_included=True, '
                   'max_included=True, msg=None)',
         'unit': '%'}
    ],
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

GOAL_2 = {
    'uuid': "407b03b1-63c6-49b2-adaf-4df5c0090047",
    'name': "COST_OPTIMIZATION",
    'display_name': 'Cost Optimization',
    'efficacy_specification': [
        {'description': 'Indicator 2', 'name': 'indicator2',
         'schema': 'Range(min=0, max=100, min_included=True, '
                   'max_included=True, msg=None)',
         'unit': '%'}
    ],
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}


class GoalShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.GOAL_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.GOAL_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.GOAL_FIELDS
    FIELD_LABELS = resource_fields.GOAL_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_goal_manager = mock.patch.object(
            resource, 'GoalManager')
        self.m_goal_mgr_cls = p_goal_manager.start()
        self.addCleanup(p_goal_manager.stop)

        self.m_goal_mgr = mock.Mock()
        self.m_goal_mgr_cls.return_value = self.m_goal_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_goal_list(self):
        goal1 = resource.Goal(mock.Mock(), GOAL_1)
        goal2 = resource.Goal(mock.Mock(), GOAL_2)
        self.m_goal_mgr.list.return_value = [
            goal1, goal2]

        exit_code, results = self.run_cmd('goal list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(goal1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(goal2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_goal_mgr.list.assert_called_once_with(detail=False)

    def test_do_goal_list_marker(self):
        goal2 = resource.Goal(mock.Mock(), GOAL_2)
        self.m_goal_mgr.list.return_value = [goal2]

        exit_code, results = self.run_cmd(
            'goal list --marker fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(goal2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_goal_mgr.list.assert_called_once_with(
            detail=False,
            marker='fc087747-61be-4aad-8126-b701731ae836')

    def test_do_goal_list_detail(self):
        goal1 = resource.Goal(mock.Mock(), GOAL_1)
        goal2 = resource.Goal(mock.Mock(), GOAL_2)
        self.m_goal_mgr.list.return_value = [
            goal1, goal2]

        exit_code, results = self.run_cmd('goal list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(goal1, self.FIELDS, self.FIELD_LABELS),
             self.resource_as_dict(goal2, self.FIELDS, self.FIELD_LABELS)],
            results)

        self.m_goal_mgr.list.assert_called_once_with(detail=True)

    def test_do_goal_show_by_name(self):
        goal = resource.Goal(mock.Mock(), GOAL_1)
        self.m_goal_mgr.get.return_value = goal

        exit_code, result = self.run_cmd('goal show SERVER_CONSOLIDATION')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(goal, self.FIELDS,
                                  self.FIELD_LABELS),
            result)
        self.m_goal_mgr.get.assert_called_once_with('SERVER_CONSOLIDATION')

    def test_do_goal_show_by_uuid(self):
        goal = resource.Goal(mock.Mock(), GOAL_1)
        self.m_goal_mgr.get.return_value = goal

        exit_code, result = self.run_cmd(
            'goal show fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(goal, self.FIELDS,
                                  self.FIELD_LABELS),
            result)
        self.m_goal_mgr.get.assert_called_once_with(
            'fc087747-61be-4aad-8126-b701731ae836')
