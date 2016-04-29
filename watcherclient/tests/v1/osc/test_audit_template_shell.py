# -*- coding: utf-8 -*-
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

from watcherclient.tests.v1.osc import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields
from watcherclient import watcher as shell


AUDIT_TEMPLATE_1 = {
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'name': 'at1',
    'description': 'Audit Template 1 description',
    'host_aggregate': 5,
    'extra': {'automatic': False},
    'goal_uuid': '7568667b-51fe-4087-9eb1-29b26891036f',
    'strategy_uuid': 'bbe6b966-f98e-439b-a01a-17b9b3b8478b',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

AUDIT_TEMPLATE_2 = {
    'uuid': '2a60ca9b-09b0-40ff-8674-de8a36fc4bc8',
    'name': 'at2',
    'description': 'Audit Template 2',
    'host_aggregate': 3,
    'extra': {'automatic': False},
    'goal_uuid': '7568667b-51fe-4087-9eb1-29b26891036f',
    'strategy_uuid': None,
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}


class AuditTemplateShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = (
        resource_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS)
    FIELDS = resource_fields.AUDIT_TEMPLATE_FIELDS
    FIELD_LABELS = resource_fields.AUDIT_TEMPLATE_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_audit_template_manager = mock.patch.object(
            resource, 'AuditTemplateManager')
        self.m_audit_template_mgr_cls = p_audit_template_manager.start()
        self.addCleanup(p_audit_template_manager.stop)

        self.m_audit_template_mgr = mock.Mock()
        self.m_audit_template_mgr_cls.return_value = self.m_audit_template_mgr

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
            'audittemplate list --goal-uuid '
            '7568667b-51fe-4087-9eb1-29b26891036f')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(audit_template2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            goal_uuid='7568667b-51fe-4087-9eb1-29b26891036f',
        )

    def test_do_audit_template_list_filter_by_strategy_uuid(self):
        audit_template1 = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.list.return_value = [audit_template1]

        exit_code, results = self.run_cmd(
            'audittemplate list --strategy-uuid '
            'bbe6b966-f98e-439b-a01a-17b9b3b8478b')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit_template1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_template_mgr.list.assert_called_once_with(
            detail=False,
            strategy_uuid='bbe6b966-f98e-439b-a01a-17b9b3b8478b',
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
            'audittemplate update at1 replace host_aggregate=5')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.update.assert_called_once_with(
            'at1',
            [{'op': 'replace', 'path': '/host_aggregate', 'value': 5}])

    def test_do_audit_template_create(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 7568667b-51fe-4087-9eb1-29b26891036f')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal_uuid='7568667b-51fe-4087-9eb1-29b26891036f',
            name='at1')

    def test_do_audit_template_create_with_description(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 7568667b-51fe-4087-9eb1-29b26891036f '
            '-d "Audit Template 1 description"')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal_uuid='7568667b-51fe-4087-9eb1-29b26891036f',
            name='at1',
            description='Audit Template 1 description')

    def test_do_audit_template_create_with_aggregate(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 7568667b-51fe-4087-9eb1-29b26891036f '
            '-a 5')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal_uuid='7568667b-51fe-4087-9eb1-29b26891036f',
            name='at1',
            host_aggregate='5')

    def test_do_audit_template_create_with_extra(self):
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.create.return_value = audit_template

        exit_code, result = self.run_cmd(
            'audittemplate create at1 7568667b-51fe-4087-9eb1-29b26891036f '
            '-e automatic=true')

        self.assertEqual(0, exit_code)
        self.assertEqual(self.resource_as_dict(audit_template, self.FIELDS,
                                               self.FIELD_LABELS),
                         result)
        self.m_audit_template_mgr.create.assert_called_once_with(
            goal_uuid='7568667b-51fe-4087-9eb1-29b26891036f',
            name='at1',
            extra={'automatic': True})
