# -*- coding: utf-8 -*-
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

import mock
import six

from watcherclient import exceptions
from watcherclient import shell
from watcherclient.tests.v1 import base
from watcherclient import v1 as resource
from watcherclient.v1 import resource_fields

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

AUDIT_1 = {
    'uuid': '5869da81-4876-4687-a1ed-12cd64cf53d9',
    'deadline': None,
    'audit_type': 'ONESHOT',
    'state': 'PENDING',
    'audit_template_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'audit_template_name': 'at1',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'parameters': None,
    'interval': None,
}

AUDIT_2 = {
    'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
    'deadline': None,
    'audit_type': 'ONESHOT',
    'audit_template_uuid': '770ef053-ecb3-48b0-85b5-d55a2dbc6588',
    'audit_template_name': 'at2',
    'state': 'PENDING',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'parameters': None,
    'interval': None,
}

AUDIT_3 = {
    'uuid': '43199d0e-0712-1213-9674-5ae2af8dhgte',
    'deadline': None,
    'audit_type': 'CONTINUOUS',
    'audit_template_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'audit_template_name': 'at1',
    'state': 'PENDING',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
    'parameters': None,
    'interval': 3600,
}


class AuditShellTest(base.CommandTestCase):

    SHORT_LIST_FIELDS = resource_fields.AUDIT_SHORT_LIST_FIELDS
    SHORT_LIST_FIELD_LABELS = resource_fields.AUDIT_SHORT_LIST_FIELD_LABELS
    FIELDS = resource_fields.AUDIT_FIELDS
    FIELD_LABELS = resource_fields.AUDIT_FIELD_LABELS

    def setUp(self):
        super(self.__class__, self).setUp()

        p_audit_manager = mock.patch.object(resource, 'AuditManager')
        p_audit_template_manager = mock.patch.object(
            resource, 'AuditTemplateManager')
        self.m_audit_mgr_cls = p_audit_manager.start()
        self.m_audit_template_mgr_cls = p_audit_template_manager.start()
        self.addCleanup(p_audit_manager.stop)
        self.addCleanup(p_audit_template_manager.stop)

        self.m_audit_mgr = mock.Mock()
        self.m_audit_template_mgr = mock.Mock()

        self.m_audit_mgr_cls.return_value = self.m_audit_mgr
        self.m_audit_template_mgr_cls.return_value = self.m_audit_template_mgr

        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_audit_list(self):
        audit1 = resource.Audit(mock.Mock(), AUDIT_1)
        audit2 = resource.Audit(mock.Mock(), AUDIT_2)
        self.m_audit_mgr.list.return_value = [
            audit1, audit2]

        exit_code, results = self.run_cmd('audit list')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit1, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS),
             self.resource_as_dict(audit2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_mgr.list.assert_called_once_with(detail=False)

    def test_do_audit_list_detail(self):
        audit1 = resource.Audit(mock.Mock(), AUDIT_1)
        audit2 = resource.Audit(mock.Mock(), AUDIT_2)
        self.m_audit_mgr.list.return_value = [
            audit1, audit2]

        exit_code, results = self.run_cmd('audit list --detail')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit1, self.FIELDS,
                                   self.FIELD_LABELS),
             self.resource_as_dict(audit2, self.FIELDS,
                                   self.FIELD_LABELS)],
            results)

        self.m_audit_mgr.list.assert_called_once_with(detail=True)

    def test_do_audit_show_by_uuid(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        self.m_audit_mgr.get.return_value = audit
        self.m_audit_template_mgr.get.return_value = audit

        exit_code, result = self.run_cmd(
            'audit show 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.get.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_audit_show_by_not_uuid(self):
        self.m_audit_mgr.get.side_effect = exceptions.HTTPNotFound

        exit_code, result = self.run_cmd(
            'audit show not_uuid', formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_audit_delete(self):
        self.m_audit_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audit delete 5869da81-4876-4687-a1ed-12cd64cf53d9',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_mgr.delete.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_audit_delete_multiple(self):
        self.m_audit_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audit delete 5869da81-4876-4687-a1ed-12cd64cf53d9 '
            '5b157edd-5a7e-4aaa-b511-f7b33ec86e9f',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_mgr.delete.assert_any_call(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')
        self.m_audit_mgr.delete.assert_any_call(
            '5b157edd-5a7e-4aaa-b511-f7b33ec86e9f')

    def test_do_audit_delete_with_not_uuid(self):
        self.m_audit_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audit delete not_uuid',
            formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_audit_update(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        self.m_audit_mgr.update.return_value = audit

        exit_code, result = self.run_cmd(
            'audit update 5869da81-4876-4687-a1ed-12cd64cf53d9 '
            'replace state=PENDING')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.update.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9',
            [{'op': 'replace', 'path': '/state', 'value': 'PENDING'}])

    def test_do_audit_update_with_not_uuid(self):
        self.m_audit_mgr.update.return_value = ''

        exit_code, result = self.run_cmd(
            'audit update not_uuid replace state=PENDING', formatting=None)

        self.assertEqual(1, exit_code)
        self.assertEqual('', result)

    def test_do_audit_create_with_audit_template_uuid(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT')

    def test_do_audit_create_with_audit_template_name(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd('audit create -a at1')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT')

    def test_do_audit_create_with_deadline(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a at1 -d 2016-04-28T10:48:32.064802')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT',
            deadline='2016-04-28T10:48:32.064802')

    def test_do_audit_create_with_type(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a at1 -t ONESHOT')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT')

    def test_do_audit_create_with_parameter(self):
        audit = resource.Audit(mock.Mock(), AUDIT_1)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a at1 -p para1=10 -p para2=20')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT',
            parameters={'para1': 10, 'para2': 20})

    def test_do_audit_create_with_type_continuous(self):
        audit = resource.Audit(mock.Mock(), AUDIT_3)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a at1 -t CONTINUOUS -i 3600')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='CONTINUOUS',
            interval='3600')
