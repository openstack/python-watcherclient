# -*- coding: utf-8 -*-
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.

import re
import sys

import fixtures
from keystoneclient import exceptions as keystone_exc
import mock
import six
from testtools import matchers

from watcherclient import exceptions as exc
from watcherclient import shell as watcher_shell
from watcherclient.tests import utils

FAKE_ENV = {'OS_USERNAME': 'username',
            'OS_PASSWORD': 'password',
            'OS_TENANT_NAME': 'tenant_name',
            'OS_AUTH_URL': 'http://no.where/v2.0/'}


class ShellTest(utils.BaseTestCase):
    re_options = re.DOTALL | re.MULTILINE

    # Patch os.environ to avoid required auth info.
    def make_env(self, exclude=None):
        env = dict((k, v) for k, v in FAKE_ENV.items() if k != exclude)
        self.useFixture(fixtures.MonkeyPatch('os.environ', env))

    def setUp(self):
        super(ShellTest, self).setUp()

    def shell(self, argstr):
        orig = sys.stdout
        try:
            sys.stdout = six.StringIO()
            _shell = watcher_shell.WatcherShell()
            _shell.main(argstr.split())
        except SystemExit:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            self.assertEqual(0, exc_value.code)
        finally:
            out = sys.stdout.getvalue()
            sys.stdout.close()
            sys.stdout = orig
        return out

    def test_help_unknown_command(self):
        self.assertRaises(exc.CommandError, self.shell, 'help foofoo')

    def test_help(self):
        required = [
            '.*?^usage: watcher',
            '.*?^ +bash-completion',
            '.*?^See "watcher help COMMAND" '
            'for help on a specific command',
        ]
        for argstr in ['--help', 'help']:
            help_text = self.shell(argstr)
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r,
                                                      self.re_options))

    def test_help_on_subcommand(self):
        required = [
            '.*?^usage: watcher action-show',
            ".*?^Show detailed information about an action",
        ]
        argstrings = [
            'help action-show',
        ]
        for argstr in argstrings:
            help_text = self.shell(argstr)
            for r in required:
                self.assertThat(help_text,
                                matchers.MatchesRegex(r, self.re_options))

    def test_auth_param(self):
        self.make_env(exclude='OS_USERNAME')
        self.test_help()

    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
    @mock.patch('getpass.getpass', return_value='password')
    def test_password_prompted(self, mock_getpass, mock_stdin):
        self.make_env(exclude='OS_PASSWORD')
        # We will get a Connection Refused because there is no keystone.
        self.assertRaises(keystone_exc.ConnectionRefused,
                          self.shell, 'action-list')
        # Make sure we are actually prompted.
        mock_getpass.assert_called_with('OpenStack Password: ')

    @mock.patch('sys.stdin', side_effect=mock.MagicMock)
    @mock.patch('getpass.getpass', side_effect=EOFError)
    def test_password_prompted_ctrlD(self, mock_getpass, mock_stdin):
        self.make_env(exclude='OS_PASSWORD')
        # We should get Command Error because we mock Ctl-D.
        self.assertRaises(exc.CommandError,
                          self.shell, 'action-list')
        # Make sure we are actually prompted.
        mock_getpass.assert_called_with('OpenStack Password: ')

    @mock.patch('sys.stdin')
    def test_no_password_no_tty(self, mock_stdin):
        # delete the isatty attribute so that we do not get
        # prompted when manually running the tests
        del mock_stdin.isatty
        required = ('You must provide a password'
                    ' via either --os-password, env[OS_PASSWORD],'
                    ' or prompted response',)
        self.make_env(exclude='OS_PASSWORD')
        try:
            self.shell('action-list')
        except exc.CommandError as message:
            self.assertEqual(required, message.args)
        else:
            self.fail('CommandError not raised')

    def test_bash_completion(self):
        stdout = self.shell('bash-completion')
        # just check we have some output
        required = [
            '.*help',
            '.*audit-list',
            '.*audit-show',
            '.*audit-delete',
            '.*audit-update',
            '.*audit-template-create',
            '.*audit-template-update',
            '.*audit-template-list',
            '.*audit-template-show',
            '.*audit-template-delete',
            '.*action-list',
            '.*action-show',
            '.*action-update',
            '.*action-plan-list',
            '.*action-plan-show',
            '.*action-plan-update',
        ]
        for r in required:
            self.assertThat(stdout,
                            matchers.MatchesRegex(r, self.re_options))
