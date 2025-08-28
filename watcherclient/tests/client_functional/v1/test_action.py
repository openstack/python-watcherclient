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


class ActionUpdateTests(base.TestCase):
    """Functional tests for action update functionality."""

    # Use API version 1.5 for action update tests
    api_version = 1.5
    dummy_name = 'dummy'
    audit_template_name = 'b' + uuidutils.generate_uuid()
    audit_uuid = None
    action_uuid = None

    @classmethod
    def setUpClass(cls):
        # Create audit template
        template_raw_output = cls.watcher(
            'audittemplate create %s dummy -s dummy' % cls.audit_template_name)
        template_output = cls.parse_show_as_object(template_raw_output)

        # Create audit
        audit_output = cls.parse_show_as_object(cls.watcher(
            'audit create -a %s' % template_output['Name']))
        cls.audit_uuid = audit_output['UUID']

        # Wait for audit to complete
        audit_created = test_utils.call_until_true(
            func=functools.partial(cls.has_audit_created, cls.audit_uuid),
            duration=600,
            sleep_for=2)
        if not audit_created:
            raise Exception('Audit has not been succeeded')

        # Get an action to test updates on
        action_list = cls.parse_show(cls.watcher('action list --audit %s'
                                                 % cls.audit_uuid))
        if action_list:
            cls.action_uuid = list(action_list[0])[0]

    @classmethod
    def tearDownClass(cls):
        # Clean up: Delete Action Plan and all related actions
        if cls.audit_uuid:
            output = cls.parse_show(
                cls.watcher('actionplan list --audit %s' % cls.audit_uuid))
            if output:
                action_plan_uuid = list(output[0])[0]
                raw_output = cls.watcher(
                    'actionplan delete %s' % action_plan_uuid)
                cls.assertOutput('', raw_output)

            # Delete audit
            raw_output = cls.watcher('audit delete %s' % cls.audit_uuid)
            cls.assertOutput('', raw_output)

        # Delete template
        raw_output = cls.watcher(
            'audittemplate delete %s' % cls.audit_template_name)
        cls.assertOutput('', raw_output)

    def test_action_update_with_state_and_reason(self):
        """Test updating action state with reason using API 1.5"""
        if not self.action_uuid:
            self.skipTest("No actions available for testing")

        # Update action state to SKIPPED with reason
        raw_output = self.watcher(
            'action update --state SKIPPED --reason "Functional test skip" %s'
            % self.action_uuid)

        # Verify the action was updated
        action = self.parse_show_as_object(
            self.watcher('action show %s' % self.action_uuid))
        self.assertEqual('SKIPPED', action['State'])
        self.assertEqual('Action skipped by user. Reason: Functional test '
                         'skip', action['Status Message'])

        # Verify output contains the action UUID
        self.assertIn(self.action_uuid, raw_output)

    def test_action_update_with_state_only(self):
        """Test updating action state without reason"""
        if not self.action_uuid:
            self.skipTest("No actions available for testing")

        # Update action state to SKIPPED without reason
        raw_output = self.watcher(
            'action update --state SKIPPED %s' % self.action_uuid)

        # Verify the action was updated
        action = self.parse_show_as_object(
            self.watcher('action show %s' % self.action_uuid))
        self.assertEqual('SKIPPED', action['State'])

        # Verify output contains the action UUID
        self.assertIn(self.action_uuid, raw_output)

    def test_action_update_missing_state_fails(self):
        """Test that action update fails when no state is provided"""
        if not self.action_uuid:
            self.skipTest("No actions available for testing")

        # This should fail because --state is required
        raw_output = self.watcher(
            'action update %s' % self.action_uuid, fail_ok=True)

        # Should contain error message about missing state
        self.assertIn(
            'At least one field update is required for this operation',
            raw_output)

    def test_action_update_nonexistent_action_fails(self):
        """Test that action update fails for non-existent action"""
        fake_uuid = uuidutils.generate_uuid()

        # This should fail because the action doesn't exist
        raw_output = self.watcher(
            'action update --state SKIPPED %s' % fake_uuid, fail_ok=True)

        # Should contain error message about action not found
        self.assertIn('404', raw_output)


class ActionUpdateApiVersionTests(base.TestCase):
    """Test action update functionality with different API versions."""

    # Use API version 1.0 to test version checking
    api_version = 1.0

    def test_action_update_unsupported_api_version(self):
        """Test that action update fails with API version < 1.5"""
        fake_uuid = uuidutils.generate_uuid()

        # This should fail because API version 1.0 doesn't support updates
        raw_output = self.watcher(
            'action update --state SKIPPED %s' % fake_uuid, fail_ok=True)

        # Should contain error message about unsupported API version
        self.assertIn('not supported in API version', raw_output)
        self.assertIn('Minimum required version is 1.5', raw_output)
