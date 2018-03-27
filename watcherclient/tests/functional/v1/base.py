#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os

import re
import shlex
import subprocess
import testtools

import six
from tempest import clients
from tempest.common import credentials_factory as creds_factory
from tempest.lib.cli import output_parser
from tempest.lib import exceptions


def credentials():
    # You can get credentials either from tempest.conf file or
    # from OS environment.
    tempest_creds = clients.get_auth_provider(
        creds_factory.get_configured_admin_credentials())
    creds = tempest_creds.credentials
    creds_dict = {
        '--os-username': os.environ.get('OS_USERNAME', creds.username),
        '--os-password': os.environ.get('OS_PASSWORD', creds.password),
        '--os-project-name': os.environ.get('OS_PROJECT_NAME',
                                            creds.project_name),
        '--os-auth-url': os.environ.get('OS_AUTH_URL',
                                        tempest_creds.auth_url),
        '--os-project-domain-name': os.environ.get('OS_PROJECT_DOMAIN_ID',
                                                   creds.project_domain_name),
        '--os-user-domain-name': os.environ.get('OS_USER_DOMAIN_ID',
                                                creds.user_domain_name),
    }
    return [x for sub in creds_dict.items() for x in sub]


def execute(cmd, fail_ok=False, merge_stderr=False):
    """Executes specified command for the given action."""
    cmdlist = shlex.split(cmd)
    cmdlist.extend(credentials())
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT if merge_stderr else subprocess.PIPE
    proc = subprocess.Popen(cmdlist, stdout=stdout, stderr=stderr)
    result, result_err = proc.communicate()
    result = result.decode('utf-8')
    if not fail_ok and proc.returncode != 0:
        raise exceptions.CommandFailed(proc.returncode, cmd, result,
                                       result_err)
    return result


class TestCase(testtools.TestCase):

    delimiter_line = re.compile('^\+\-[\+\-]+\-\+$')

    @classmethod
    def watcher(cls, cmd, fail_ok=False):
        """Executes watcherclient command for the given action."""
        return execute('watcher {0}'.format(cmd), fail_ok=fail_ok)

    @classmethod
    def get_opts(cls, fields, format='value'):
        return ' -f {0} {1}'.format(format,
                                    ' '.join(['-c ' + it for it in fields]))

    @classmethod
    def assertOutput(cls, expected, actual):
        if expected != actual:
            raise Exception('{0} != {1}'.format(expected, actual))

    @classmethod
    def assertInOutput(cls, expected, actual):
        if expected not in actual:
            raise Exception('{0} not in {1}'.format(expected, actual))

    def assert_table_structure(self, items, field_names):
        """Verify that all items have keys listed in field_names."""
        for item in items:
            for field in field_names:
                self.assertIn(field, item)

    def assert_show_fields(self, items, field_names):
        """Verify that all items have keys listed in field_names."""
        for item in items:
            for key in six.iterkeys(item):
                self.assertIn(key, field_names)

    def assert_show_structure(self, items, field_names):
        """Verify that all field_names listed in keys of all items."""
        if isinstance(items, list):
            o = {}
            for d in items:
                o.update(d)
        else:
            o = items
        item_keys = o.keys()
        for field in field_names:
            self.assertIn(field, item_keys)

    @staticmethod
    def parse_show_as_object(raw_output):
        """Return a dict with values parsed from cli output."""
        items = TestCase.parse_show(raw_output)
        o = {}
        for item in items:
            o.update(item)
        return o

    @staticmethod
    def parse_show(raw_output):
        """Return list of dicts with item values parsed from cli output."""

        items = []
        table_ = output_parser.table(raw_output)
        for row in table_['values']:
            item = {}
            item[row[0]] = row[1]
            items.append(item)
        return items

    def parse_listing(self, raw_output):
        """Return list of dicts with basic item parsed from cli output."""
        return output_parser.listing(raw_output)

    def has_actionplan_succeeded(self, ap_uuid):
        return self.parse_show_as_object(
            self.watcher('actionplan show %s' % ap_uuid)
        )['State'] == 'SUCCEEDED'

    @classmethod
    def has_audit_created(cls, audit_uuid):
        return cls.parse_show_as_object(
            cls.watcher('audit show %s' % audit_uuid))['State'] == 'SUCCEEDED'
