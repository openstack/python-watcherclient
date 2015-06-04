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
from watcherclient.openstack.common import cliutils
from watcherclient.tests import utils
import watcherclient.v1.audit_template_shell as at_shell


class AuditTemplateShellTest(utils.BaseTestCase):
    def test_do_audit_template_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            audit_template = object()
            at_shell._print_audit_template_show(audit_template)
        exp = [
            'uuid', 'created_at', 'updated_at', 'deleted_at',
            'description', 'host_aggregate', 'name',
            'extra', 'goal']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_audit_template_show_by_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'audit-template', 'a5199d0e-0702-4613-9234-5ae2af8dafea')

        at_shell.do_audit_template_show(client_mock, args)
        client_mock.audit_template.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea'
        )
        # assert get_by_name() wasn't called
        self.assertFalse(client_mock.audit_template.get_by_name.called)

    def test_do_audit_template_show_by_name(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'audit-template', "a5199d0e-0702-4613-9234-5ae2af8dafea")

        at_shell.do_audit_template_show(client_mock, args)
        client_mock.audit_template.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea')

    def test_do_audit_template_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'audit-template',
                ['a5199d0e-0702-4613-9234-5ae2af8dafea'])

        at_shell.do_audit_template_delete(client_mock, args)
        client_mock.audit_template.delete.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea')

    def test_do_audit_template_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'audit-template',
                ['a5199d0e-0702-4613-9234-5ae2af8dafea',
                 'a5199d0e-0702-4613-9234-5ae2af8dafeb'])

        at_shell.do_audit_template_delete(client_mock, args)
        client_mock.audit_template.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea'),
             mock.call('a5199d0e-0702-4613-9234-5ae2af8dafeb')])

    def test_do_audit_template_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'audit-template', "a5199d0e-0702-4613-9234-5ae2af8dafea")
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        at_shell.do_audit_template_update(client_mock, args)
        patch = commonutils.args_array_to_patch(
            args.op,
            args.attributes[0])
        client_mock.audit_template.update.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea', patch)

    def test_do_audit_template_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        at_shell.do_audit_template_create(client_mock, args)
        client_mock.audit_template.create.assert_called_once_with()

    def test_do_audit_template_create_with_name(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.name = 'my audit template'

        at_shell.do_audit_template_create(client_mock, args)
        client_mock.audit_template.create.assert_called_once_with(
            name='my audit template')

    def test_do_audit_template_create_with_description(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.description = 'description'

        at_shell.do_audit_template_create(client_mock, args)
        client_mock.audit_template.create.assert_called_once_with(
            description='description')

    def test_do_audit_template_create_with_aggregate(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.host_aggregate = 5

        at_shell.do_audit_template_create(client_mock, args)
        client_mock.audit_template.create.assert_called_once_with(
            host_aggregate=5)

    def test_do_audit_template_create_with_extra(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.extra = ['automatic=true']

        at_shell.do_audit_template_create(client_mock, args)
        client_mock.audit_template.create.assert_called_once_with(
            extra={'automatic': True})
