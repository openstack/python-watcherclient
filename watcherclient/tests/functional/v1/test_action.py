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
        audit_output = cls.parse_show_as_object(cls.watcher(
            'audit create -a %s' % template_output['Name']))
        cls.audit_uuid = audit_output['UUID']
        audit_created = test_utils.call_until_true(
            func=functools.partial(cls.has_audit_created, cls.audit_uuid),
            duration=600,
            sleep_for=2)
        if not audit_created:
            raise Exception('Audit has not been succeeded')

    @classmethod
    def tearDownClass(cls):
        # Delete Action Plan and all related actions.
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

    def test_action_list(self):
        raw_output = self.watcher('action list')
        self.assert_table_structure([raw_output], self.list_fields)

    def test_action_detailed_list(self):
        raw_output = self.watcher('action list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_action_show(self):
        action_list = self.parse_show(self.watcher('action list --audit %s'
                                      % self.audit_uuid))
        action_uuid = list(action_list[0])[0]
        action = self.watcher('action show %s' % action_uuid)
        self.assertIn(action_uuid, action)
        self.assert_table_structure([action],
                                    self.detailed_list_fields)
