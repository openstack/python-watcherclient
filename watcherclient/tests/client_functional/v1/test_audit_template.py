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

from watcherclient.tests.client_functional.v1 import base
from watcherclient.tests.client_functional.v1.base import execute


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


class AuditTemplateDefaultParametersTests(base.TestCase):
    """Functional tests for audit template default_parameters (API v1.7)."""

    api_version = 1.7
    audit_template_name = 'c' + uuidutils.generate_uuid()
    list_fields = ['UUID', 'Name', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + [
        'Created At', 'Updated At', 'Deleted At',
        'Description', 'Audit Scope', 'Default Parameters',
    ]

    def _create_with_default_params(self):
        return self.watcher(
            'audittemplate create %s dummy -s dummy -p para1=5.0'
            % self.audit_template_name)

    def _delete(self):
        self.watcher('audittemplate delete %s' % self.audit_template_name,
                     fail_ok=True)

    def test_create_with_default_parameters(self):
        raw_output = self._create_with_default_params()
        self.assert_table_structure([raw_output], self.detailed_list_fields)
        parsed = self.parse_show_as_object(raw_output)
        self.assertIn('para1', parsed['Default Parameters'])
        self._delete()

    def test_show_includes_default_parameters(self):
        self._create_with_default_params()
        raw_output = self.watcher('audittemplate show %s'
                                  % self.audit_template_name)
        self.assert_table_structure([raw_output], self.detailed_list_fields)
        parsed = self.parse_show_as_object(raw_output)
        self.assertIn('para1', parsed['Default Parameters'])
        self._delete()

    def test_detailed_list_includes_default_parameters(self):
        self._create_with_default_params()
        raw_output = self.watcher('audittemplate list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)
        self._delete()

    def test_old_microversion_hides_default_parameters(self):
        self._create_with_default_params()
        raw_output = execute(
            'openstack optimize --os-infra-optim-api-version 1.6 '
            'audittemplate show %s' % self.audit_template_name)
        parsed = self.parse_show_as_object(raw_output)
        self.assertNotIn('para1', parsed.get('Default Parameters', ''))
        self._delete()
