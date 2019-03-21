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

from oslo_utils.uuidutils import generate_uuid
from watcherclient import exceptions
from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

ACTION_PLAN_1 = {
    'uuid': 'd9d9978e-6db5-4a05-8eab-1531795d7004',
    'audit_uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'strategy_name': 'dummy',
    'state': 'RECOMMENDED',
    'efficacy_indicators': [{'description': 'Indicator 1',
                             'name': 'indicator1',
                             'unit': '%'}],
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'global_efficacy': [
        {"value": 99,
         "unit": "%",
         "name": "dummy_global_efficacy",
         "description": "Dummy Global Efficacy"},
        {"value": 75,
         "unit": "%",
         "name": "dummy_global_efficacy2",
         "description": "Dummy Global Efficacy2"}
        ],
    'deleted_at': None,
    'hostname': ''
}

ACTION_PLAN_2 = {
    'uuid': 'd6363285-5afa-4a26-96f2-89441e335765',
    'audit_uuid': '239f02a5-9649-4e14-9d33-ac2bf67cb755',
    'strategy_name': 'dummy',
    'state': 'RECOMMENDED',
    'created_at': datetime.datetime.now().isoformat(),
    'efficacy_indicators': [{'description': 'Indicator 2',
                             'name': 'indicator2',
                             'unit': '%'}],
    'updated_at': None,
    'global_efficacy': [{
        "value": 87,
        "unit": "%",
        "name": "dummy_global_efficacy",
        "description": "Dummy Global Efficacy",
    }],
    'deleted_at': None,
    'hostname': ''
}


class ActionPlanShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.ACTION_PLAN_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.ACTION_PLAN_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.ACTION_PLAN_FIELDS
    FIELD_LABELS = resource_fields.ACTION_PLAN_FIELD_LABELS
    GLOBAL_EFFICACY_FIELDS = resource_fields.GLOBAL_EFFICACY_FIELDS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_audit_manager = mock.patch.object(resource, 'AuditManager')
        p_audit_template_manager = mock.patch.object(
            resource, 'ActionPlanManager')
        p_action_plan_manager = mock.patch.object(
            resource, 'ActionPlanManager')

        self.m_audit_mgr_cls = p_audit_manager.start()
        self.m_audit_template_mgr_cls = p_audit_template_manager.start()
        self.m_action_plan_mgr_cls = p_action_plan_manager.start()

        self.addCleanup(p_audit_manager.stop)
        self.addCleanup(p_audit_template_manager.stop)
        self.addCleanup(p_action_plan_manager.stop)

        self.m_audit_mgr = mock.Mock()
        self.m_audit_template_mgr = mock.Mock()
        self.m_action_plan_mgr = mock.Mock()

        self.m_audit_mgr_cls.return_value = self.m_audit_mgr
        self.m_audit_template_mgr_cls.return_value = self.m_audit_template_mgr
        self.m_action_plan_mgr_cls.return_value = self.m_action_plan_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_action_plan_list(self):
        action_plan1 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        action_plan2 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_2)
        self.m_action_plan_mgr.list.return_value = [
            action_plan1, action_plan2]

        exit_code, results = self.run_cmd('actionplan list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action_plan1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(action_plan2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.assertEqual(action_plan1.global_efficacy,
                         results[0]['Global efficacy'])
        self.assertEqual(action_plan2.global_efficacy,
                         results[1]['Global efficacy'])

    def test_do_action_plan_list_by_table(self):
        action_plan1 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        action_plan2 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_2)
        self.m_action_plan_mgr.list.return_value = [
            action_plan1, action_plan2]

        exit_code, results = self.run_cmd('actionplan list', 'table')
        self.assertEqual(0, exit_code)
        self.assertIn(ACTION_PLAN_1['uuid'], results)
        self.assertIn(ACTION_PLAN_2['uuid'], results)

        self.m_action_plan_mgr.list.assert_called_once_with(detail=False)

    def test_do_action_plan_list_detail(self):
        action_plan1 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        action_plan2 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_2)
        self.m_action_plan_mgr.list.return_value = [
            action_plan1, action_plan2]

        exit_code, results = self.run_cmd('actionplan list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action_plan1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(action_plan2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)
        self.assertEqual(action_plan1.global_efficacy,
                         results[0]['Global efficacy'])
        self.assertEqual(action_plan2.global_efficacy,
                         results[1]['Global efficacy'])

        self.m_action_plan_mgr.list.assert_called_once_with(detail=True)

    def test_do_action_plan_list_filter_by_audit(self):
        action_plan1 = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.list.return_value = [action_plan1]

        exit_code, results = self.run_cmd(
            'actionplan list --audit '
            '770ef053-ecb3-48b0-85b5-d55a2dbc6588')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(action_plan1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_action_plan_mgr.list.assert_called_once_with(
            detail=False,
            audit='770ef053-ecb3-48b0-85b5-d55a2dbc6588',
        )

    def test_do_action_plan_show_by_uuid(self):
        action_plan = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.get.return_value = action_plan

        exit_code, result = self.run_cmd(
            'actionplan show d9d9978e-6db5-4a05-8eab-1531795d7004')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(
                action_plan, self.FIELDS, self.FIELD_LABELS),
            result)
        self.assertEqual(action_plan.global_efficacy,
                         result['Global efficacy'])
        self.m_action_plan_mgr.get.assert_called_once_with(
            'd9d9978e-6db5-4a05-8eab-1531795d7004')

    def test_do_action_plan_show_by_not_uuid(self):
        self.m_action_plan_mgr.get.side_effect = exceptions.HTTPNotFound

        exit_code, result = self.run_cmd(
            'actionplan show not_uuid', formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_plan_show_by_random_uuid(self):
        # verify that show a wrong actionplan will raise Exception
        self.m_action_plan_mgr.get.side_effect = exceptions.HTTPNotFound
        fake_uuid = generate_uuid()

        exit_code, result = self.run_cmd(
            'actionplan show {}'.format(fake_uuid), formatting=None)
        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

        self.m_action_plan_mgr.get.assert_called_once_with(fake_uuid)

    def test_do_action_plan_show_uuid_by_table(self):
        # verify that show an actionplan can be in a 'table' format
        action_plan = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.get.return_value = action_plan

        exit_code, result = self.run_cmd(
            'actionplan show d9d9978e-6db5-4a05-8eab-1531795d7004',
            formatting='table')
        self.assertEqual(0, exit_code)
        self.assertIn(ACTION_PLAN_1['uuid'], result)

        self.m_action_plan_mgr.get.assert_called_once_with(
            'd9d9978e-6db5-4a05-8eab-1531795d7004')

    def test_do_action_plan_delete(self):
        self.m_action_plan_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'actionplan delete 5869da81-4876-4687-a1ed-12cd64cf53d9',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_action_plan_mgr.delete.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_action_plan_delete_not_uuid(self):
        exit_code, result = self.run_cmd(
            'actionplan delete not_uuid', formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_plan_delete_multiple(self):
        self.m_action_plan_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'actionplan delete 5869da81-4876-4687-a1ed-12cd64cf53d9 '
            'c20627fa-ea70-4d56-ae15-4106358f773b',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_action_plan_mgr.delete.assert_any_call(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')
        self.m_action_plan_mgr.delete.assert_any_call(
            'c20627fa-ea70-4d56-ae15-4106358f773b')

    def test_do_action_plan_update(self):
        action_plan = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.update.return_value = action_plan

        exit_code, result = self.run_cmd(
            'actionplan update 5869da81-4876-4687-a1ed-12cd64cf53d9 '
            'replace state=CANCELLED')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action_plan, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_action_plan_mgr.update.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9',
            [{'op': 'replace', 'path': '/state', 'value': 'CANCELLED'}])

    def test_do_action_plan_update_not_uuid(self):
        exit_code, result = self.run_cmd(
            'actionplan update not_uuid '
            'replace state=CANCELLED',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_plan_start(self):
        action_plan = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.start.return_value = action_plan

        exit_code, result = self.run_cmd(
            'actionplan start 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action_plan, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_action_plan_mgr.start.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_action_plan_start_not_uuid(self):
        exit_code, result = self.run_cmd(
            'actionplan start not_uuid',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_action_plan_cancel(self):
        action_plan = resource.ActionPlan(mock.Mock(), ACTION_PLAN_1)
        self.m_action_plan_mgr.cancel.return_value = action_plan

        exit_code, result = self.run_cmd(
            'actionplan cancel 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(action_plan, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_action_plan_mgr.cancel.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_action_plan_cancel_not_uuid(self):
        exit_code, result = self.run_cmd(
            'actionplan cancel not_uuid',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)
