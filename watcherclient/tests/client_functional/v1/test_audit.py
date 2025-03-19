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

from datetime import datetime
from dateutil import tz
import functools

from oslo_utils import uuidutils
from tempest.lib.common.utils import test_utils

from watcherclient.tests.client_functional.v1 import base


class AuditTests(base.TestCase):
    """Functional tests for audit."""

    dummy_name = 'dummy'
    list_fields = ['UUID', 'Name', 'Audit Type', 'State', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Parameters',
                                          'Interval', 'Audit Scope',
                                          'Next Run Time', 'Hostname']
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
        audit_created = test_utils.call_until_true(
            func=functools.partial(cls.has_audit_created, cls.audit_uuid),
            duration=600,
            sleep_for=2)
        if not audit_created:
            raise Exception('Audit has not been succeeded')

    @classmethod
    def tearDownClass(cls):
        output = cls.parse_show(
            cls.watcher('actionplan list --audit %s' % cls.audit_uuid))
        action_plan_uuid = list(output[0])[0]
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


class AuditTestsV11(AuditTests):
    """This class tests v1.1 of Watcher API"""

    api_version = 1.1

    detailed_list_fields = AuditTests.list_fields + [
        'Created At', 'Updated At', 'Deleted At', 'Parameters', 'Interval',
        'Audit Scope', 'Next Run Time', 'Hostname', 'Start Time', 'End Time']

    def test_audit_detailed_list(self):
        raw_output = self.watcher('audit list --detail')
        self.assert_table_structure([raw_output], self.detailed_list_fields)

    def test_audit_show(self):
        audit = self.watcher('audit show ' + self.audit_uuid)
        self.assertIn(self.audit_uuid, audit)
        self.assert_table_structure([audit], self.detailed_list_fields)

    def test_audit_update(self):
        local_time = datetime.now(tz.tzlocal())
        local_time_str = local_time.strftime("%Y-%m-%dT%H:%M:%S")
        utc_time = (local_time - local_time.utcoffset())
        utc_time_str = utc_time.strftime("%Y-%m-%dT%H:%M:%S")
        audit_raw_output = self.watcher(
            'audit update {0} replace end_time="{1}"'.format(self.audit_uuid,
                                                             local_time_str))
        audit_output = self.parse_show_as_object(audit_raw_output)
        assert audit_output['End Time'] == utc_time_str


class AuditTestsV12(AuditTestsV11):
    """This class tests v1.2 of Watcher API"""

    api_version = 1.2

    @classmethod
    def setUpClass(cls):
        raw_output = cls.watcher('audittemplate create %s dummy -s dummy'
                                 % cls.audit_template_name)
        template_output = cls.parse_show_as_object(raw_output)
        audit_raw_output = cls.watcher(
            'audit create --force -a %s' % template_output['Name'])
        audit_output = cls.parse_show_as_object(audit_raw_output)
        cls.audit_uuid = audit_output['UUID']
        audit_created = test_utils.call_until_true(
            func=functools.partial(cls.has_audit_created, cls.audit_uuid),
            duration=600,
            sleep_for=2)
        if not audit_created:
            raise Exception('Audit has not been succeeded')


class AuditActiveTests(base.TestCase):

    list_fields = ['UUID', 'Name', 'Audit Type', 'State', 'Goal', 'Strategy']
    detailed_list_fields = list_fields + ['Created At', 'Updated At',
                                          'Deleted At', 'Parameters',
                                          'Interval', 'Audit Scope']
    audit_template_name = 'a' + uuidutils.generate_uuid()

    @classmethod
    def setUpClass(cls):
        cls.watcher('audittemplate create %s dummy -s dummy'
                    % cls.audit_template_name)

    @classmethod
    def tearDownClass(cls):
        cls.watcher('audittemplate delete %s' % cls.audit_template_name)

    def _create_audit(self):
        return self.parse_show_as_object(
            self.watcher('audit create -a %s'
                         % self.audit_template_name))['UUID']

    def _delete_audit(self, audit_uuid):
        self.assertTrue(test_utils.call_until_true(
            func=functools.partial(
                self.has_audit_created, audit_uuid),
            duration=600,
            sleep_for=2
        ))
        output = self.parse_show(
            self.watcher('actionplan list --audit %s' % audit_uuid))
        action_plan_uuid = list(output[0])[0]
        self.watcher('actionplan delete %s' % action_plan_uuid)
        self.watcher('audit delete %s' % audit_uuid)

    def test_create_oneshot_audit(self):
        audit = self.watcher('audit create -a %s' % self.audit_template_name)
        audit_uuid = self.parse_show_as_object(audit)['UUID']
        self.assert_table_structure([audit], self.detailed_list_fields)
        self._delete_audit(audit_uuid)

    def test_delete_oneshot_audit(self):
        audit_uuid = self._create_audit()
        self.assertTrue(test_utils.call_until_true(
            func=functools.partial(
                self.has_audit_created, audit_uuid),
            duration=600,
            sleep_for=2
        ))
        raw_output = self.watcher('audit delete %s' % audit_uuid)
        self.assertOutput('', raw_output)
        output = self.parse_show(
            self.watcher('actionplan list --audit %s' % audit_uuid))
        action_plan_uuid = list(output[0])[0]
        self.watcher('actionplan delete %s' % action_plan_uuid)

    def test_continuous_audit(self):
        audit = self.watcher('audit create -a %s -t CONTINUOUS -i 600'
                             % self.audit_template_name)
        audit_uuid = self.parse_show_as_object(audit)['UUID']
        self.assert_table_structure([audit], self.detailed_list_fields)
        self.assertTrue(test_utils.call_until_true(
            func=functools.partial(
                self.has_audit_created, audit_uuid),
            duration=600,
            sleep_for=2
        ))
        audit_state = self.parse_show_as_object(
            self.watcher('audit show %s' % audit_uuid))['State']
        if audit_state == 'ONGOING':
            self.watcher('audit update %s replace state=CANCELLED'
                         % audit_uuid)
        raw_output = self.watcher('audit delete %s' % audit_uuid)
        self.assertOutput('', raw_output)
        outputs = self.parse_listing(
            self.watcher('actionplan list --audit %s' % audit_uuid))
        for actionplan in outputs:
            self.watcher('actionplan delete %s' % actionplan['UUID'])
