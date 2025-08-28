#
# Copyright 2013 IBM Corp
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import datetime
import io
import unittest
from unittest import mock

from watcherclient import exceptions
from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

ACTION_1 = {
    'uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'action_plan_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'state': 'PENDING',
    'action_type': 'migrate',
    'parents': ['239f02a5-9649-4e14-9d33-ac2bf67cb755'],
    'input_parameters': {"test": 1},
    'description': 'test',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

ACTION_2 = {
    'uuid': '239f02a5-9649-4e14-9d33-ac2bf67cb755',
    'action_plan_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'state': 'PENDING',
    'action_type': 'migrate',
    'parents': ['67653274-eb24-c7ba-70f6-a84e73d80843'],
    'input_parameters': {"test": 2},
    'description': 'test',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

ACTION_3 = {
    'uuid': '67653274-eb24-c7ba-70f6-a84e73d80843',
    'action_plan_uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'parents': [],
    'state': 'PENDING',
    'action_type': 'sleep',
    'description': 'test',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

ACTION_PLAN_1 = {
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'action': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'state': 'RECOMMENDED',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}


class ActionShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.ACTION_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = resource_fields.ACTION_SHORT_LIST_FIELD_LABELS
    FIELDS = resource_fields.ACTION_FIELDS
    FIELD_LABELS = resource_fields.ACTION_FIELD_LABELS

    def setUp(self, os_infra_optim_api_version='1.0'):
        super(ActionShellTest, self).setUp(
            os_infra_optim_api_version=os_infra_optim_api_version)

        p_action_manager = mock.patch.object(resource, 'ActionManager')
        p_action_plan_manager = mock.patch.object(
            resource, 'ActionPlanManager')
        self.m_action_mgr_cls = p_action_manager.start()
        self.m_action_plan_mgr_cls = p_action_plan_manager.start()
        self.addCleanup(p_action_manager.stop)
        self.addCleanup(p_action_plan_manager.stop)

        self.m_action_mgr = mock.Mock()
        self.m_action_plan_mgr = mock.Mock()

        self.m_action_mgr_cls.return_value = self.m_action_mgr
        self.m_action_plan_mgr_cls.return_value = self.m_action_plan_mgr

        self.stdout = io.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_action_list(self):
        action1 = resource.Action(mock.Mock(), ACTION_1)
        action2 = resource.Action(mock.Mock(), ACTION_2)
        self.m_action_mgr.list.return_value = [action1, action2]

        exit_code, results = self.run_cmd('action list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(action2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_action_mgr.list.assert_called_once_with(detail=False)

    def test_do_action_list_detail(self):
        action1 = resource.Action(mock.Mock(), ACTION_1)
        action2 = resource.Action(mock.Mock(), ACTION_2)
        self.m_action_mgr.list.return_value = [action1, action2]

        exit_code, results = self.run_cmd('action list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(action2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)

        self.m_action_mgr.list.assert_called_once_with(detail=True)

    def test_do_action_list_marker(self):
        action2 = resource.Action(mock.Mock(), ACTION_2)
        action3 = resource.Action(mock.Mock(), ACTION_3)
        self.m_action_mgr.list.return_value = [
            action2, action3]

        exit_code, results = self.run_cmd(
            'action list --marker 770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(action3, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_action_mgr.list.assert_called_once_with(
            detail=False,
            marker='770ef053-ecb3-48b0-85b5-d55a2dbc6588')

    def test_do_action_show_by_uuid(self):
        action = resource.Action(mock.Mock(), ACTION_1)
        self.m_action_mgr.get.return_value = action
        self.m_action_plan_mgr.get.return_value = action

        exit_code, result = self.run_cmd(
            'action show 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_action_mgr.get.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_action_show_by_not_uuid(self):
        self.m_action_mgr.get.side_effect = exceptions.HTTPNotFound

        exit_code, result = self.run_cmd(
            'action show not_uuid', formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_update_unsupported_version(self):

        exit_code, result = self.run_cmd(
            'action update --state SKIPPED '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)


class ActionShellTest15(ActionShellTest):
    def setUp(self):
        super(ActionShellTest15, self).setUp(os_infra_optim_api_version='1.5')
        v15 = dict(status_message=None)
        for action in (ACTION_1, ACTION_2, ACTION_3):
            action.update(v15)
        self.FIELDS.extend(['status_message'])
        self.FIELD_LABELS.extend(['Status Message'])

    def test_do_action_update_with_state_only(self):
        action = resource.Action(mock.Mock(), ACTION_1)
        self.m_action_mgr.update.return_value = action

        exit_code, result = self.run_cmd(
            'action update --state SKIPPED '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action, self.FIELDS, self.FIELD_LABELS),
            result)

        expected_patch = [
            {'op': 'replace', 'path': '/state', 'value': 'SKIPPED'}
        ]
        self.m_action_mgr.update.assert_called_once_with(
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588', expected_patch)

    def test_do_action_update_with_state_and_reason(self):
        action = resource.Action(mock.Mock(), ACTION_1)
        self.m_action_mgr.update.return_value = action

        exit_code, result = self.run_cmd(
            'action update --state SKIPPED --reason "Manual skip" '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action, self.FIELDS, self.FIELD_LABELS),
            result)

        expected_patch = [
            {'op': 'replace', 'path': '/state', 'value': 'SKIPPED'},
            {'op': 'replace', 'path': '/status_message',
             'value': 'Manual skip'}
        ]
        self.m_action_mgr.update.assert_called_once_with(
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588', expected_patch)

    def test_do_action_update_with_reason_only(self):
        action = resource.Action(mock.Mock(), ACTION_1)
        self.m_action_mgr.update.return_value = action

        exit_code, result = self.run_cmd(
            'action update --reason "Manual skip" '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action, self.FIELDS, self.FIELD_LABELS),
            result)

        expected_patch = [
            {'op': 'replace', 'path': '/status_message',
             'value': 'Manual skip'}
        ]
        self.m_action_mgr.update.assert_called_once_with(
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588', expected_patch)

    def test_do_action_update_no_fields_to_update(self):
        exit_code, result = self.run_cmd(
            'action update 770ef053-ecb3-48b0-85b5-d55a2dbc6588',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_update_action_not_found(self):

        self.m_action_mgr.update.side_effect = exceptions.HTTPNotFound

        exit_code, result = self.run_cmd(
            'action update --state SKIPPED not_found_uuid',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    @unittest.skip("Action update is supported in API version 1.5")
    def test_do_action_update_unsupported_version(self):
        pass
