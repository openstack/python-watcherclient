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


class ActionPlanTests(base.TestCase):
    """Functional tests for action plan."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Audit', 'State', 'Updated At', 'Global efficacy']
    detailed_list_fields = list_fields + ['Created At', 'Deleted At',
                                          'Strategy', 'Efficacy indicators']
    audit_template_name = 'a' + uuidutils.generate_uuid()
    audit_uuid = None

    @classmethod
    def setUpClass(cls):
        template_raw_output = cls.watcher(
            'audittemplate create %s dummy -s dummy' % cls.audit_template_name)
        template_output = cls.parse_show_as_object(template_raw_output)
        audit_raw_output = cls.watcher('audit create -a %s'
                                       % template_output['Name'])
        audit_output = cls.parse_show_as_object(audit_raw_output)
        cls.audit_uuid = audit_output['UUID']

    @classmethod
    def tearDownClass(cls):
        # Delete action plan
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

    def test_action_plan_list(self):
        raw_output = self.watcher('actionplan list')
        self.assert_table_structure([raw_output], self.list_fields)

    def test_action_plan_detailed_list(self):
        raw_output = self.watcher('actionplan list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_action_plan_show(self):
        action_plan_list = self.parse_show(self.watcher('actionplan list'))
        action_plan_uuid = action_plan_list[0].keys()[0]
        actionplan = self.watcher('actionplan show %s' % action_plan_uuid)
        self.assertIn(action_plan_uuid, actionplan)
        self.assert_table_structure([actionplan],
                                    self.detailed_list_fields)

    def test_action_plan_start(self):
        output = self.parse_show(self.watcher('actionplan list --audit %s'
                                              % self.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        self.watcher('actionplan start %s' % action_plan_uuid)
        raw_output = self.watcher('actionplan show %s' % action_plan_uuid)
        self.assert_table_structure([raw_output], self.detailed_list_fields)


class ActionPlanActiveTests(base.TestCase):

    audit_uuid = None
    audit_template_name = 'b' + uuidutils.generate_uuid()

    list_fields = ['UUID', 'Audit', 'State', 'Updated At', 'Global efficacy']
    detailed_list_fields = list_fields + ['Created At', 'Deleted At',
                                          'Strategy', 'Efficacy indicators']

    def _delete_action_plan(self):
        output = self.parse_show(
            self.watcher('actionplan list --audit %s' % self.audit_uuid))
        action_plan_uuid = output[0].keys()[0]
        raw_output = self.watcher('actionplan delete %s' % action_plan_uuid)
        self.assertOutput('', raw_output)

    def _delete_audit(self):
        raw_output = self.watcher('audit delete %s' % self.audit_uuid)
        self.assertOutput('', raw_output)

    def _delete_audit_template(self):
        raw_output = self.watcher(
            'audittemplate delete %s' % self.audit_template_name)
        self.assertOutput('', raw_output)

    def _create_audit_template(self):
        template_raw_output = self.watcher(
            'audittemplate create %s dummy -s dummy'
            % self.audit_template_name)
        template_output = self.parse_show_as_object(template_raw_output)
        return template_output

    def test_action_plan_create(self):
        template_output = self._create_audit_template()
        action_plan = self.watcher(
            'actionplan create -a %s' % template_output['Name'])
        self.audit_uuid = self.parse_show_as_object(action_plan)['UUID']
        self.assert_table_structure([action_plan], self.detailed_list_fields)
        self._delete_action_plan()
        self._delete_audit()
        self._delete_audit_template()
