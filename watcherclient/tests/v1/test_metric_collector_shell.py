# -*- coding: utf-8 -*-
#
# Copyright 2013 IBM Corp
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

import mock

from watcherclient.common import utils as commonutils
from watcherclient.openstack.common import cliutils
from watcherclient.tests import utils
import watcherclient.v1.metric_collector_shell as mc_shell


class MetricCollectorShellTest(utils.BaseTestCase):
    def test_do_metric_collector_show(self):
        actual = {}
        fake_print_dict = lambda data, *args, **kwargs: actual.update(data)
        with mock.patch.object(cliutils, 'print_dict', fake_print_dict):
            metric_collector = object()
            mc_shell._print_metric_collector_show(metric_collector)
        exp = ['uuid', 'created_at', 'updated_at', 'deleted_at',
               'category', 'endpoint']
        act = actual.keys()
        self.assertEqual(sorted(exp), sorted(act))

    def test_do_metric_collector_show_by_uuid(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.metric_collector = 'a5199d0e-0702-4613-9234-5ae2af8dafea'

        mc_shell.do_metric_collector_show(client_mock, args)
        client_mock.metric_collector.get.assert_called_once_with(
            'a5199d0e-0702-4613-9234-5ae2af8dafea'
        )
        # assert get_by_name() wasn't called
        self.assertFalse(client_mock.metric_collector.get_by_name.called)

    def test_do_metric_collector_delete(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.metric_collector = ['metric_collector_uuid']

        mc_shell.do_metric_collector_delete(client_mock, args)
        client_mock.metric_collector.delete.assert_called_once_with(
            'metric_collector_uuid'
        )

    def test_do_metric_collector_delete_multiple(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.metric_collector = ['metric_collector_uuid1',
                                 'metric_collector_uuid2']

        mc_shell.do_metric_collector_delete(client_mock, args)
        client_mock.metric_collector.delete.assert_has_calls(
            [mock.call('metric_collector_uuid1'),
             mock.call('metric_collector_uuid2')])

    def test_do_metric_collector_update(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        setattr(args, 'metric-collector', "metric_collector_uuid")
        args.op = 'add'
        args.attributes = [['arg1=val1', 'arg2=val2']]

        mc_shell.do_metric_collector_update(client_mock, args)
        patch = commonutils.args_array_to_patch(
            args.op,
            args.attributes[0])
        client_mock.metric_collector.update.assert_called_once_with(
            'metric_collector_uuid', patch)

    def test_do_metric_collector_create(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()

        mc_shell.do_metric_collector_create(client_mock, args)
        client_mock.metric_collector.create.assert_called_once_with()

    def test_do_metric_collector_create_with_category(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.category = 'mc_category'

        mc_shell.do_metric_collector_create(client_mock, args)
        client_mock.metric_collector.create.assert_called_once_with(
            category='mc_category')

    def test_do_metric_collector_create_with_endpoint(self):
        client_mock = mock.MagicMock()
        args = mock.MagicMock()
        args.endpoint = 'mc_endpoint'

        mc_shell.do_metric_collector_create(client_mock, args)
        client_mock.metric_collector.create.assert_called_once_with(
            endpoint='mc_endpoint')
