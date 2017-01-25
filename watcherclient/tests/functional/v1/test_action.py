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


class ActionTests(base.TestCase):
    """Functional tests for action."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Parents', 'State', 'Action Plan', 'Action']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Parameters']
    audit_template_name = 'a' + uuidutils.generate_uuid()
    audit_uuid = None

    @classmethod
    def setUpClass(cls):
        template_raw_output = cls.watcher(
            'audittemplate create %s dummy -s dummy' % cls.audit_template_name)
        template_output = cls.parse_show_as_object(template_raw_output)
        audit_raw_output = cls.watcher(
            'audit create -a %s' % template_output['Name'])
        audit_output = cls.parse_show_as_object(audit_raw_output)
        cls.audit_uuid = audit_output['UUID']

    @classmethod
    def tearDownClass(cls):
        # Delete Action Plan and all related actions.
        output = cls.parse_show(
            cls.watcher('actionplan list --audit %s' % cls.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        raw_output = cls.watcher('actionplan delete %s' % action_plan_uuid)
        cls.assertOutput('', raw_output)
        # Delete audit
        raw_output = cls.watcher('audit delete %s' % cls.audit_uuid)
        cls.assertOutput('', raw_output)
        # Delete Template
        raw_output = cls.watcher(
            'audittemplate delete %s' % cls.audit_template_name)
        cls.assertOutput('', raw_output)

    def test_action_list(self):
        raw_output = self.watcher('action list')
        self.assert_table_structure([raw_output], self.list_fields)

    def test_action_detailed_list(self):
        raw_output = self.watcher('action list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_action_show(self):
        action_list = self.parse_show(self.watcher('action list'))
        action_uuid = action_list[0].keys()[0]
        action = self.watcher('action show ' + action_uuid)
        self.assertIn(action_uuid, action)
        self.assert_table_structure([action],
                                    self.detailed_list_fields)
