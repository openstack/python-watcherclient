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

import functools

from tempest.lib.common.utils import test_utils

from watcherclient.tests.client_functional.v1 import base


class ActionPlanTests(base.TestCase):
    """Functional tests for action plan."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Audit', 'State', 'Updated At', 'Global efficacy']
    detailed_list_fields = list_fields + ['Created At', 'Deleted At',
                                          'Strategy', 'Efficacy indicators',
                                          'Hostname']
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
        audit_created = test_utils.call_until_true(
            func=functools.partial(cls.has_audit_created, cls.audit_uuid),
            duration=600,
            sleep_for=2)
        if not audit_created:
            raise Exception('Audit has not been succeeded')

    @classmethod
    def tearDownClass(cls):
        # Delete action plan
        output = cls.parse_show(
            cls.watcher('actionplan list --audit %s' % cls.audit_uuid))
        action_plan_uuid = list(output[0])[0]
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
        action_plan_uuid = list(action_plan_list[0])[0]
        actionplan = self.watcher('actionplan show %s' % action_plan_uuid)
        self.assertIn(action_plan_uuid, actionplan)
        self.assert_table_structure([actionplan],
                                    self.detailed_list_fields)

    def test_action_plan_start(self):
        output = self.parse_show(self.watcher('actionplan list --audit %s'
                                              % self.audit_uuid))
        action_plan_uuid = list(output[0])[0]
        self.watcher('actionplan start %s' % action_plan_uuid)
        raw_output = self.watcher('actionplan show %s' % action_plan_uuid)
        self.assert_table_structure([raw_output], self.detailed_list_fields)

        self.assertTrue(test_utils.call_until_true(
            func=functools.partial(
                self.has_actionplan_succeeded, action_plan_uuid),
            duration=600,
            sleep_for=2
        ))
