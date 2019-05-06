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

from watcherclient import shell
from watcherclient.tests.unit.v1 import base
from watcherclient import v1 as resource

AUDIT_TEMPLATE_1 = {
    'uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
    'name': 'at1',
    'description': 'Audit Template 1 description',
    'goal_uuid': 'fc087747-61be-4aad-8126-b701731ae836',
    'strategy_uuid': '2cf86250-d309-4b81-818e-1537f3dba6e5',
    'created_at': datetime.datetime.now().isoformat(),
    'updated_at': None,
    'deleted_at': None,
}

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


class AuditShellTest(base.CommandTestCase):

    AUDIT_1 = {
        'uuid': '5869da81-4876-4687-a1ed-12cd64cf53d9',
        'audit_type': 'ONESHOT',
        'state': 'PENDING',
        'audit_template_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
        'audit_template_name': 'at1',
        'goal_name': 'SERVER_CONSOLIDATION',
        'strategy_name': 'basic',
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': None,
        'deleted_at': None,
        'parameters': None,
        'interval': None,
        'scope': '',
        'auto_trigger': False,
        'next_run_time': None,
        'name': 'my_audit1',
        'hostname': '',
    }

    AUDIT_2 = {
        'uuid': 'a5199d0e-0702-4613-9234-5ae2af8dafea',
        'audit_type': 'ONESHOT',
        'state': 'PENDING',
        'audit_template_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
        'audit_template_name': 'at1',
        'goal_name': 'fc087747-61be-4aad-8126-b701731ae836',
        'strategy_name': 'auto',
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': None,
        'deleted_at': None,
        'parameters': None,
        'interval': None,
        'scope': '',
        'auto_trigger': False,
        'next_run_time': None,
        'name': 'my_audit2',
        'hostname': '',
    }

    AUDIT_3 = {
        'uuid': '43199d0e-0712-1213-9674-5ae2af8dhgte',
        'audit_type': 'ONESHOT',
        'state': 'PENDING',
        'audit_template_uuid': 'f8e47706-efcf-49a4-a5c4-af604eb492f2',
        'audit_template_name': 'at1',
        'goal_name': None,
        'strategy_name': 'auto',
        'created_at': datetime.datetime.now().isoformat(),
        'updated_at': None,
        'deleted_at': None,
        'parameters': None,
        'interval': 3600,
        'scope': '',
        'auto_trigger': True,
        'next_run_time': None,
        'name': 'my_audit3',
        'hostname': '',
    }

    SHORT_LIST_FIELDS = ['uuid', 'name', 'audit_type',
                         'state', 'goal_name', 'strategy_name',
                         'auto_trigger']
    SHORT_LIST_FIELD_LABELS = ['UUID', 'Name', 'Audit Type', 'State', 'Goal',
                               'Strategy', 'Auto Trigger']
    FIELDS = ['uuid', 'name', 'created_at', 'updated_at', 'deleted_at',
              'state', 'audit_type', 'parameters', 'interval', 'goal_name',
              'strategy_name', 'scope', 'auto_trigger', 'next_run_time',
              'hostname']
    FIELD_LABELS = ['UUID', 'Name', 'Created At', 'Updated At', 'Deleted At',
                    'State', 'Audit Type', 'Parameters', 'Interval', 'Goal',
                    'Strategy', 'Audit Scope', 'Auto Trigger',
                    'Next Run Time', 'Hostname']

    def setUp(self, os_infra_optim_api_version='1.0'):
        super(AuditShellTest, self).setUp(
            os_infra_optim_api_version=os_infra_optim_api_version)

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

        # stdout mock
        self.stdout = six.StringIO()
        self.cmd = shell.WatcherShell(stdout=self.stdout)

    def test_do_audit_list(self):
        audit1 = resource.Audit(mock.Mock(), self.AUDIT_1)
        audit2 = resource.Audit(mock.Mock(), self.AUDIT_2)
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

    def test_do_audit_list_marker(self):
        audit2 = resource.Audit(mock.Mock(), self.AUDIT_2)
        self.m_audit_mgr.list.return_value = [audit2]

        exit_code, results = self.run_cmd(
            'audit list --marker 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            [self.resource_as_dict(audit2, self.SHORT_LIST_FIELDS,
                                   self.SHORT_LIST_FIELD_LABELS)],
            results)

        self.m_audit_mgr.list.assert_called_once_with(
            detail=False,
            marker='5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_audit_list_detail(self):
        audit1 = resource.Audit(mock.Mock(), self.AUDIT_1)
        audit2 = resource.Audit(mock.Mock(), self.AUDIT_2)
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
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.get.return_value = audit

        exit_code, result = self.run_cmd(
            'audit show 5869da81-4876-4687-a1ed-12cd64cf53d9')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.get.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_audit_show_by_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.get.return_value = audit

        exit_code, result = self.run_cmd(
            'audit show my_audit')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.get.assert_called_once_with(
            'my_audit')

    def test_do_audit_delete(self):
        self.m_audit_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audit delete 5869da81-4876-4687-a1ed-12cd64cf53d9',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_mgr.delete.assert_called_once_with(
            '5869da81-4876-4687-a1ed-12cd64cf53d9')

    def test_do_audit_delete_by_name(self):
        self.m_audit_mgr.delete.return_value = ''

        exit_code, result = self.run_cmd(
            'audit delete my_audit',
            formatting=None)

        self.assertEqual(0, exit_code)
        self.assertEqual('', result)
        self.m_audit_mgr.delete.assert_called_once_with(
            'my_audit')

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

    def test_do_audit_update(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
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

    def test_do_audit_update_by_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.update.return_value = audit

        exit_code, result = self.run_cmd(
            'audit update my_audit replace state=PENDING')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.update.assert_called_once_with(
            'my_audit',
            [{'op': 'replace', 'path': '/state', 'value': 'PENDING'}])

    def test_do_audit_create_with_audit_template_uuid(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_3)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT',
            auto_trigger=False
        )

    def test_do_audit_create_with_audit_template_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_3)
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
            auto_trigger=False,
            audit_type='ONESHOT'
        )

    def test_do_audit_create_with_goal(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            auto_trigger=False,
            audit_type='ONESHOT'
        )

    def test_do_audit_create_with_goal_and_strategy(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -s '
            '2cf86250-d309-4b81-818e-1537f3dba6e5')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            strategy='2cf86250-d309-4b81-818e-1537f3dba6e5',
            auto_trigger=False,
            audit_type='ONESHOT'
        )

    def test_do_audit_create_with_type(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -t ONESHOT')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            auto_trigger=False,
            audit_type='ONESHOT'
        )

    def test_do_audit_create_with_parameter(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -p para1=10 '
            '-p para2=20')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='ONESHOT',
            auto_trigger=False,
            parameters={'para1': 10, 'para2': 20}
        )

    def test_do_audit_create_with_type_continuous(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 '
            '-t CONTINUOUS -i 3600')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='CONTINUOUS',
            auto_trigger=False,
            interval='3600'
        )

    def test_do_audit_create_with_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 '
            '-t CONTINUOUS -i 3600 --name my_audit')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='CONTINUOUS',
            auto_trigger=False,
            interval='3600',
            name='my_audit'
        )


class AuditShellTestv11(AuditShellTest):
    def setUp(self):
        super(AuditShellTestv11, self).setUp(os_infra_optim_api_version='1.1')
        v11 = dict(start_time=None, end_time=None)
        for audit in (self.AUDIT_1, self.AUDIT_2, self.AUDIT_3):
            audit.update(v11)
        self.FIELDS.extend(['start_time', 'end_time'])
        self.FIELD_LABELS.extend(['Start Time', 'End Time'])


class AuditShellTestv12(AuditShellTest):
    def setUp(self):
        super(AuditShellTestv12, self).setUp(os_infra_optim_api_version='1.2')
        v11 = dict(start_time=None, end_time=None)
        v12 = dict(force=False)
        for audit in (self.AUDIT_1, self.AUDIT_2, self.AUDIT_3):
            audit.update(v11)
            audit.update(v12)
        self.FIELDS.extend(['start_time', 'end_time', 'force'])
        self.FIELD_LABELS.extend(['Start Time', 'End Time', 'Force'])

    def test_do_audit_create_with_force(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_3)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a f8e47706-efcf-49a4-a5c4-af604eb492f2 --force')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT',
            auto_trigger=False,
            force=True
        )

    def test_do_audit_create_with_audit_template_uuid(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_3)
        audit_template = resource.AuditTemplate(mock.Mock(), AUDIT_TEMPLATE_1)
        self.m_audit_template_mgr.get.return_value = audit_template
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -a f8e47706-efcf-49a4-a5c4-af604eb492f2')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            audit_template_uuid='f8e47706-efcf-49a4-a5c4-af604eb492f2',
            audit_type='ONESHOT',
            auto_trigger=False,
            force=False
        )

    def test_do_audit_create_with_audit_template_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_3)
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
            auto_trigger=False,
            audit_type='ONESHOT',
            force=False
        )

    def test_do_audit_create_with_goal(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            auto_trigger=False,
            audit_type='ONESHOT',
            force=False
        )

    def test_do_audit_create_with_goal_and_strategy(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -s '
            '2cf86250-d309-4b81-818e-1537f3dba6e5')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            strategy='2cf86250-d309-4b81-818e-1537f3dba6e5',
            auto_trigger=False,
            audit_type='ONESHOT',
            force=False
        )

    def test_do_audit_create_with_type(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -t ONESHOT')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            auto_trigger=False,
            audit_type='ONESHOT',
            force=False
        )

    def test_do_audit_create_with_parameter(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 -p para1=10 '
            '-p para2=20')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='ONESHOT',
            auto_trigger=False,
            parameters={'para1': 10, 'para2': 20},
            force=False
        )

    def test_do_audit_create_with_type_continuous(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 '
            '-t CONTINUOUS -i 3600')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='CONTINUOUS',
            auto_trigger=False,
            interval='3600',
            force=False
        )

    def test_do_audit_create_with_name(self):
        audit = resource.Audit(mock.Mock(), self.AUDIT_1)
        self.m_audit_mgr.create.return_value = audit

        exit_code, result = self.run_cmd(
            'audit create -g fc087747-61be-4aad-8126-b701731ae836 '
            '-t CONTINUOUS -i 3600 --name my_audit')

        self.assertEqual(0, exit_code)
        self.assertEqual(
            self.resource_as_dict(audit, self.FIELDS, self.FIELD_LABELS),
            result)
        self.m_audit_mgr.create.assert_called_once_with(
            goal='fc087747-61be-4aad-8126-b701731ae836',
            audit_type='CONTINUOUS',
            auto_trigger=False,
            interval='3600',
            name='my_audit',
            force=False
        )
