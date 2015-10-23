# -*- coding: utf-8 -*-
#
# Copyright 2013 IBM Corp
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
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
import watcherclient.v1.audit_shell as a_shell


class AuditShellTest(utils.BaseTestCase):
    def test_do_audit_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            audit = object()
            a_shell._print_audit_show(audit)
        exp = ['created_at', 'audit_template_uuid', 'audit_template_name',
               'updated_at', 'uuid', 'deleted_at', 'state', 'type',
               'deadline']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_audit_show_by_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = 'a5199d0e-0702-4613-9234-5ae2af8dafea'

        a_shell.do_audit_show(client_mock, args)
        client_mock.audit.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea'
        )
        # assert get_by_name() wasn't called
        self.assertFalse(client_mock.audit.get_by_name.called)

    def test_do_audit_show_by_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = 'not_uuid'

        self.assertRaises(ValidationError, a_shell.do_audit_show,
                          client_mock, args)

    def test_do_audit_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = ['a5199d0e-0702-4613-9234-5ae2af8dafea']

        a_shell.do_audit_delete(client_mock, args)
        client_mock.audit.delete.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea')

    def test_do_audit_delete_with_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = ['not_uuid']

        self.assertRaises(ValidationError, a_shell.do_audit_delete,
                          client_mock, args)

    def test_do_audit_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = ['a5199d0e-0702-4613-9234-5ae2af8dafea',
                      'a5199d0e-0702-4613-9234-5ae2af8dafeb']

        a_shell.do_audit_delete(client_mock, args)
        client_mock.audit.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea'),
             mock.call('a5199d0e-0702-4613-9234-5ae2af8dafeb')])

    def test_do_audit_delete_multiple_with_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = ['a5199d0e-0702-4613-9234-5ae2af8dafea',
                      'not_uuid',
                      'a5199d0e-0702-4613-9234-5ae2af8dafeb']

        self.assertRaises(ValidationError, a_shell.do_audit_delete,
                          client_mock, args)
        client_mock.audit.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea')])

    def test_do_audit_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = 'a5199d0e-0702-4613-9234-5ae2af8dafea'
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        a_shell.do_audit_update(client_mock, args)
        patch = commonutils.args_array_to_patch(
            args.op,
            args.attributes[0])
        client_mock.audit.update.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea', patch)

    def test_do_audit_update_with_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.audit = ['not_uuid']
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        self.assertRaises(ValidationError, a_shell.do_audit_update,
                          client_mock, args)

    def test_do_audit_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        a_shell.do_audit_create(client_mock, args)
        client_mock.audit.create.assert_called_once_with()

    def test_do_audit_create_with_deadline(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.deadline = 'deadline'

        a_shell.do_audit_create(client_mock, args)
        client_mock.audit.create.assert_called_once_with(
            deadline='deadline')

    def test_do_audit_create_with_type(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.type = 'type'

        a_shell.do_audit_create(client_mock, args)
        client_mock.audit.create.assert_called_once_with(type='type')
