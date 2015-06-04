# -*- coding: utf-8 -*-
#
# Copyright 2013 IBM Corp
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
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
import watcherclient.v1.action_plan_shell as ap_shell


class ActionPlanShellTest(utils.BaseTestCase):
    def test_do_action_plan_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            action_plan = object()
            ap_shell._print_action_plan_show(action_plan)
        exp = ['uuid', 'created_at', 'updated_at', 'deleted_at',
               'state', 'audit_uuid']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_action_plan_show_by_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'action-plan', 'a5199d0e-0702-4613-9234-5ae2af8dafea')

        ap_shell.do_action_plan_show(client_mock, args)
        client_mock.action_plan.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea'
        )
        # assert get_by_name() wasn't called
        self.assertFalse(client_mock.action_plan.get_by_name.called)

    def test_do_action_plan_show_by_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'action-plan', 'not_uuid')

        self.assertRaises(ValidationError, ap_shell.do_action_plan_show,
                          client_mock, args)

    def test_do_action_plan_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        delete = ['a5199d0e-0702-4613-9234-5ae2af8dafea']
        setattr(args, 'action-plan', delete)

        ap_shell.do_action_plan_delete(client_mock, args)
        client_mock.action_plan.delete.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea')

    def test_do_action_plan_delete_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'action-plan', ['not_uuid'])

        self.assertRaises(ValidationError, ap_shell.do_action_plan_delete,
                          client_mock, args)

    def test_do_action_plan_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'action-plan',
                ["a5199d0e-0702-4613-9234-5ae2af8dafea",
                 "a5199d0e-0702-4613-9234-5ae2af8dafeb"])

        ap_shell.do_action_plan_delete(client_mock, args)
        client_mock.action_plan.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea'),
             mock.call('a5199d0e-0702-4613-9234-5ae2af8dafeb')])

    def test_do_action_plan_delete_multiple_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'action-plan',
                ["a5199d0e-0702-4613-9234-5ae2af8dafea",
                 "not_uuid",
                 "a5199d0e-0702-4613-9234-5ae2af8dafeb"])

        self.assertRaises(ValidationError, ap_shell.do_action_plan_delete,
                          client_mock, args)
        client_mock.action_plan.delete.assert_has_calls(
            [mock.call('a5199d0e-0702-4613-9234-5ae2af8dafea')])

    def test_do_action_plan_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        setattr(args, 'action-plan', "a5199d0e-0702-4613-9234-5ae2af8dafea")
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        ap_shell.do_action_plan_update(client_mock, args)
        patch = commonutils.args_array_to_patch(
            args.op,
            args.attributes[0])
        client_mock.action_plan.update.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea', patch)

    def test_do_action_plan_update_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        setattr(args, 'action-plan', "not_uuid")
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        self.assertRaises(ValidationError, ap_shell.do_action_plan_update,
                          client_mock, args)

    def test_do_action_plan_start(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        action_plan = 'a5199d0e-0702-4613-9234-5ae2af8dafea'
        setattr(args, 'action-plan', action_plan)

        ap_shell.do_action_plan_start(client_mock, args)
        patch = commonutils.args_array_to_patch(
            'replace', ['state=STARTING'])
        client_mock.action_plan.update.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea', patch)

    def test_do_action_plan_start_not_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        action_plan = 'not_uuid'
        setattr(args, 'action-plan', action_plan)

        self.assertRaises(ValidationError, ap_shell.do_action_plan_start,
                          client_mock, args)
