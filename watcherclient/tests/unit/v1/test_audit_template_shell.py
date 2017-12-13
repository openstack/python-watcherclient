#
# Copyright 2013 IBM Corp
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
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
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

STRATEGY_1 = {
    'uuid': '2cf86250-d309-4b81-818e-1537f3dba6e5',
    'name': 'basic',
    'display_name': 'Basic consolidation',
    'goal_uuid': 'fc087747-61be-4aad-8126-b701731ae836',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

AUDIT_TEMPLATE_1 = {
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'name': 'at1',
    'description': 'Audit Template 1 description',
    'goal_uuid': 'fc087747-61be-4aad-8126-b701731ae836',
    'goal_name': 'SERVER_CONSOLIDATION',
    'strategy_uuid': '2cf86250-d309-4b81-818e-1537f3dba6e5',
    'strategy_name': 'basic',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'scope': []
}

AUDIT_TEMPLATE_2 = {
    'uuid': '2a60ca9b-09b0-40ff-8674-de8a36fc4bc8',
    'name': 'at2',
    'description': 'Audit Template 2',
    'goal_uuid': 'fc087747-61be-4aad-8126-b701731ae836',
    'goal_name': 'SERVER_CONSOLIDATION',
    'strategy_uuid': None,
    'strategy_name': None,
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'scope': []
}


class AuditTemplateShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.AUDIT_TEMPLATE_FIELDS
    FIELD_LABELS = resource_fields.AUDIT_TEMPLATE_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        # goal mock
        p_goal_manager = mock.patch.object(resource, 'GoalManager')
        self.m_goal_mgr_cls = p_goal_manager.start()
        self.addCleanup(p_goal_manager.stop)

        self.m_goal_mgr = mock.Mock()
        self.m_goal_mgr_cls.return_value = self.m_goal_mgr

        # strategy mock
        p_strategy_manager = mock.patch.object(resource, 'StrategyManager')
        self.m_strategy_mgr_cls = p_strategy_manager.start()
        self.addCleanup(p_strategy_manager.stop)

        self.m_strategy_mgr = mock.Mock()
        self.m_strategy_mgr_cls.return_value = self.m_strategy_mgr

        # audit template mock
        p_audit_template_manager = mock.patch.object(
            resource, 'AuditTemplateManager')
        self.m_audit_template_mgr_cls = p_audit_template_manager.start()
        self.addCleanup(p_audit_template_manager.stop)

        self.m_audit_template_mgr = mock.Mock()
        self.m_audit_template_mgr_cls.return_value = self.m_audit_template_mgr

        # stdout mock
        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_audit_template_list(self):
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        audit_template2 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_2)
        self.m_audit_template_mgr.list.return_value = [
            audit_template1, audit_template2]

        exit_code, results = self.run_cmd('audittemplate list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(audit_template2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(detail=False)

    def test_do_audit_template_list_marker(self):
        audit_template2 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_2)
        self.m_audit_template_mgr.list.return_value = [audit_template2]

        exit_code, results = self.run_cmd(
            'audittemplate list --marker '
            'f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            marker='f8e47706-efcf-49a4-a5c4-af604eb492f2')

    def test_do_audit_template_list_detail(self):
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        audit_template2 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_2)
        self.m_audit_template_mgr.list.return_value = [
            audit_template1, audit_template2]

        exit_code, results = self.run_cmd('audittemplate list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(audit_template2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(detail=True)

    def test_do_audit_template_list_filter_by_goal_uuid(self):
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        audit_template2 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_2)
        self.m_audit_template_mgr.list.return_value = [
            audit_template1, audit_template2]

        exit_code, results = self.run_cmd(
            'audittemplate list --goal '
            'fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(audit_template2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            goal='fc087747-61be-4aad-8126-b701731ae836',
        )

    def test_do_audit_template_list_filter_by_goal_name(self):
        goal1 = resource.Goal(mock.Mock(), GOAL_1)
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        audit_template2 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_2)
        self.m_goal_mgr.get.return_value = goal1
        self.m_strategy_mgr.get.return_value = strategy1
        self.m_audit_template_mgr.list.return_value = [
            audit_template1, audit_template2]

        exit_code, results = self.run_cmd(
            'audittemplate list --goal SERVER_CONSOLIDATION')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(audit_template2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            goal='SERVER_CONSOLIDATION',
        )

    def test_do_audit_template_list_filter_by_strategy_uuid(self):
        goal1 = resource.Goal(mock.Mock(), GOAL_1)
        strategy1 = resource.Strategy(mock.Mock(), STRATEGY_1)
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_goal_mgr.get.return_value = goal1
        self.m_strategy_mgr.get.return_value = strategy1
        self.m_audit_template_mgr.list.return_value = [audit_template1]

        exit_code, results = self.run_cmd(
            'audittemplate list --strategy '
            '2cf86250-d309-4b81-818e-1537f3dba6e5')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            strategy='2cf86250-d309-4b81-818e-1537f3dba6e5',
        )

    def test_do_audit_template_list_filter_by_strategy_name(self):
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.list.return_value = [audit_template1]

        exit_code, results = self.run_cmd(
            'audittemplate list --strategy '
            'basic')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            strategy='basic',
        )

    def test_do_audit_template_show_by_name(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template

        exit_code, result = self.run_cmd('audittemplate show at1')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.get.assert_called_once_with('at1')

    def test_do_audit_template_show_by_uuid(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate show f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.get.assert_called_once_with(
            'f8e47706-efcf-49a4-a5c4-af604eb492f2')

    def test_do_audit_template_delete(self):
        self.m_audit_template_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audittemplate delete f8e47706-efcf-49a4-a5c4-af604eb492f2',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_template_mgr.delete.assert_called_once_with(
            'f8e47706-efcf-49a4-a5c4-af604eb492f2')

    def test_do_audit_template_delete_multiple(self):
        self.m_audit_template_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audittemplate delete f8e47706-efcf-49a4-a5c4-af604eb492f2 '
            '92dfce2f-0a5e-473f-92b7-d92e21839e4d',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_template_mgr.delete.assert_any_call(
            'f8e47706-efcf-49a4-a5c4-af604eb492f2')
        self.m_audit_template_mgr.delete.assert_any_call(
            '92dfce2f-0a5e-473f-92b7-d92e21839e4d')

    def test_do_audit_template_update(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.update.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate update at1 replace description="New description"')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.update.assert_called_once_with(
            'at1',
            [{'op': 'replace', 'path': '/description',
              'value': 'New description'}])

    def test_do_audit_template_create(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            name='at1')

    def test_do_audit_template_create_with_description(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 fc087747-61be-4aad-8126-b701731ae836 '
            '-d "Audit Template 1 description"')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            name='at1',
            description='Audit Template 1 description')

    def test_do_audit_template_create_with_aggregate(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            name='at1')
