# -*- encoding: utf-8 -*-
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


class AuditTemplateTests(base.TestCase):
    """Functional tests for audit template."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Name', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Description',
                                          'Audit Scope']
    audit_template_name = 'a' + uuidutils.generate_uuid()

    @classmethod
    def setUpClass(cls):
        cls.watcher('audittemplate create %s dummy -s dummy'
                    % cls.audit_template_name)

    @classmethod
    def tearDownClass(cls):
        cls.watcher('audittemplate delete %s' % cls.audit_template_name)

    def test_audit_template_list(self):
        raw_output = self.watcher('audittemplate list')
        self.assert_table_structure([raw_output], self.list_fields)

    def test_audit_template_detailed_list(self):
        raw_output = self.watcher('audittemplate list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_audit_template_show(self):
        audit_template = self.watcher(
            'audittemplate show %s' % self.audit_template_name)
        self.assertIn(self.audit_template_name, audit_template)
        self.assert_table_structure([audit_template],
                                    self.detailed_list_fields)

    def test_audit_template_update(self):
        raw_output = self.watcher('audittemplate update %s replace '
                                  'description="Updated Desc"'
                                  % self.audit_template_name)
        audit_template_output = self.parse_show_as_object(raw_output)
        assert audit_template_output['Description'] == 'Updated Desc'


class AuditTemplateActiveTests(base.TestCase):

    audit_template_name = 'b' + uuidutils.generate_uuid()
    list_fields = ['UUID', 'Name', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Description',
                                          'Audit Scope']

    def _create_audit_template(self):
        self.watcher('audittemplate create %s dummy -s dummy '
                     '-d "Test Audit Template"' % self.audit_template_name)

    def _delete_audit_template(self):
        self.watcher('audittemplate delete %s' % self.audit_template_name)

    def test_create_audit_template(self):
        raw_output = self.watcher('audittemplate create %s dummy '
                                  '-s dummy -d "Test Audit Template"'
                                  % self.audit_template_name)
        self.assert_table_structure([raw_output], self.detailed_list_fields)
        self._delete_audit_template()

    def test_delete_audit_template(self):
        self._create_audit_template()
        raw_output = self.watcher('audittemplate delete %s'
                                  % self.audit_template_name)
        self.assertOutput('', raw_output)
