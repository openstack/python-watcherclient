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

from oslo_utils import uuidutils

from watcherclient.tests.functional.v1 import base


class AuditTests(base.TestCase):
    """Functional tests for audit."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Audit Type', 'State', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Parameters',
                                          'Interval', 'Audit Scope']
    audit_template_name = 'a' + uuidutils.generate_uuid()
    audit_uuid = None

    @classmethod
    def setUpClass(cls):
        raw_output = cls.watcher('audittemplate create %s dummy -s dummy'
                                 % cls.audit_template_name)
        template_output = cls.parse_show_as_object(raw_output)
        audit_raw_output = cls.watcher(
            'audit create -a %s' % template_output['Name'])
        audit_output = cls.parse_show_as_object(audit_raw_output)
        cls.audit_uuid = audit_output['UUID']

    @classmethod
    def tearDownClass(cls):
        output = cls.parse_show(
            cls.watcher('actionplan list --audit %s' % cls.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        cls.watcher('actionplan delete %s' % action_plan_uuid)
        cls.watcher('audit delete %s' % cls.audit_uuid)
        cls.watcher('audittemplate delete %s' % cls.audit_template_name)

    def test_audit_list(self):
        raw_output = self.watcher('audit list')
        self.assert_table_structure([raw_output], self.list_fields)

    def test_audit_detailed_list(self):
        raw_output = self.watcher('audit list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_audit_show(self):
        audit = self.watcher('audit show ' + self.audit_uuid)
        self.assertIn(self.audit_uuid, audit)
        self.assert_table_structure([audit], self.detailed_list_fields)

    def test_audit_update(self):
        audit_raw_output = self.watcher('audit update %s add interval=2'
                                        % self.audit_uuid)
        audit_output = self.parse_show_as_object(audit_raw_output)
        assert int(audit_output['Interval']) == 2


class AuditActiveTests(base.TestCase):

    list_fields = ['UUID', 'Audit Type', 'State', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Parameters',
                                          'Interval', 'Audit Scope']
    audit_template_name = 'a' + uuidutils.generate_uuid()
    audit_uuid = None

    def _create_audit(self):
        raw_output = self.watcher('audittemplate create %s dummy -s dummy'
                                  % self.audit_template_name)
        template_output = self.parse_show_as_object(raw_output)
        self.audit_uuid = self.parse_show_as_object(
            self.watcher('audit create -a %s'
                         % template_output['Name']))['UUID']

    def _delete_audit(self):
        output = self.parse_show(
            self.watcher('actionplan list --audit %s' % self.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        self.watcher('actionplan delete %s' % action_plan_uuid)
        self.watcher('audit delete %s' % self.audit_uuid)
        self.watcher('audittemplate delete %s' % self.audit_template_name)

    def test_create_audit(self):
        raw_output = self.watcher('audittemplate create %s dummy -s dummy'
                                  % self.audit_template_name)
        template_output = self.parse_show_as_object(raw_output)
        audit = self.watcher('audit create -a %s' % template_output['Name'])
        self.audit_uuid = self.parse_show_as_object(audit)['UUID']
        self.assert_table_structure([audit], self.detailed_list_fields)
        self._delete_audit()

    def test_delete_audit(self):
        self._create_audit()
        raw_output = self.watcher('audit delete %s' % self.audit_uuid)
        self.assertOutput('', raw_output)
        output = self.parse_show(
            self.watcher('actionplan list --audit %s' % self.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        self.watcher('actionplan delete %s' % action_plan_uuid)
        self.watcher('audittemplate delete %s' % self.audit_template_name)
