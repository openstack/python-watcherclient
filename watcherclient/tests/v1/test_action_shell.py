# -*- coding: utf-8 -*-
#
# Copyright 2013 IBM Corp
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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

import mock

from watcherclient.common import utils as commonutils
from watcherclient.openstack.common.apiclient.exceptions import ValidationError
from watcherclient.openstack.common import cliutils
from watcherclient.tests import utils
import watcherclient.v1.action_shell as a_shell


class ActionShellTest(utils.BaseTestCase):
    def test_do_action_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            action = object()
            a_shell._print_action_show(action)
        exp = ['action_type',
               'alarm',
               'applies_to',
               'created_at',
               'deleted_at',
               'description',
               'dst',
               'next_uuid',
               'parameter',
               'src',
               'state',
               'action_plan_uuid',
               'updated_at',
               'uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_action_show_by_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = 'a5199d0e-0702-4613-9234-5ae2af8dafea'

        a_shell.do_action_show(client_mock, args)
        client_mock.action.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea'
        )
        # assert get_by_name() wasn't called
        self.assertFalse(client_mock.action.get_by_name.called)

    def test_do_action_show_by_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = 'not_uuid'

        self.assertRaises(ValidationError, a_shell.do_action_show,
                          client_mock, args)

    def test_do_action_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = ['a5199d0e-0702-4613-9234-5ae2af8dafea']

        a_shell.do_action_delete(client_mock, args)
        client_mock.action.delete.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea')

    def test_do_action_delete_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = ['not_uuid']

        self.assertRaises(ValidationError, a_shell.do_action_delete,
                          client_mock, args)

    def test_do_action_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = ['a5199d0e-0702-4613-9234-5ae2af8dafea',
                       'a5199d0e-0702-4613-9234-5ae2af8dafeb']

        a_shell.do_action_delete(client_mock, args)
        client_mock.action.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea'),
             mock.call('a5199d0e-0702-4613-9234-5ae2af8dafeb')])

    def test_do_action_delete_multiple_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = ['a5199d0e-0702-4613-9234-5ae2af8dafea',
                       'not_uuid'
                       'a5199d0e-0702-4613-9234-5ae2af8dafeb']

        self.assertRaises(ValidationError, a_shell.do_action_delete,
                          client_mock, args)
        client_mock.action.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea')])

    def test_do_action_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = 'a5199d0e-0702-4613-9234-5ae2af8dafea'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        a_shell.do_action_update(client_mock, args)
        patch = commonutils.args_array_to_patch(
            args.op,
            args.attributes[0])
        client_mock.action.update.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea', patch)

    def test_do_action_update_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.action = 'not_uuid'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        self.assertRaises(ValidationError, a_shell.do_action_update,
                          client_mock, args)
