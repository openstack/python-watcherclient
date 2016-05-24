# -*- encoding: utf-8 -*-
# Copyright (c) 2016 b<>com
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

import json
import shlex

import mock

from watcherclient import shell
from watcherclient.tests import utils
from watcherclient.v1 import client


class CommandTestCase(utils.BaseTestCase):

    def setUp(self):
        super(CommandTestCase, self).setUp()

        self.p_build_http_client = mock.patch.object(
            client.Client, 'build_http_client')
        self.m_build_http_client = self.p_build_http_client.start()

        self.m_watcher_client = mock.Mock(side_effect=client.Client)
        self.p_create_client = mock.patch.object(
            shell.WatcherShell, 'create_client', self.m_watcher_client)
        self.p_create_client.start()

        self.addCleanup(self.p_build_http_client.stop)
        self.addCleanup(self.p_create_client.stop)

    def run_cmd(self, cmd, formatting='json'):
        if formatting:
            formatter_arg = " -f %s" % formatting
            formatter = json.loads
        else:
            formatter_arg = ''
            formatter = str
        formatted_cmd = "%(cmd)s%(formatter)s" % dict(
            cmd=cmd, formatter=formatter_arg)

        exit_code = self.cmd.run(shlex.split(formatted_cmd))

        try:
            raw_data = self.stdout.getvalue()
            formatted_output = formatter(self.stdout.getvalue())
        except Exception:
            self.fail("Formatting error (`%s` -> '%s')" %
                      (raw_data, formatting))
        return exit_code, formatted_output

    def resource_as_dict(self, resource, columns=(), column_headers=()):
        mapping = dict(zip(columns, column_headers))
        return {mapping[k]: v for k, v in resource.to_dict().items()
                if not columns or columns and k in mapping}
