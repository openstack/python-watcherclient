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

import shlex

import mock
from osc_lib import utils as oscutils
from oslo_serialization import jsonutils

from watcherclient.common import httpclient
from watcherclient.tests.unit import utils


class CommandTestCase(utils.BaseTestCase):

    def setUp(self, os_infra_optim_api_version='1.0'):
        super(CommandTestCase, self).setUp()

        self.fake_env = {
            'debug': False,
            'insecure': False,
            'no_auth': False,
            'os_auth_token': '',
            'os_auth_url': 'http://127.0.0.1:5000/v2.0',
            'os_endpoint_override': 'http://watcher-endpoint:9322',
            'os_username': 'test',
            'os_password': 'test',
            'timeout': 600,
            'os_infra_optim_api_version': os_infra_optim_api_version}
        self.m_env = mock.Mock(
            name='m_env',
            side_effect=lambda x, *args, **kwargs: self.fake_env.get(
                x.lower(), kwargs.get('default', '')))
        self.p_env = mock.patch.object(oscutils, 'env', self.m_env)
        self.p_env.start()
        self.addCleanup(self.p_env.stop)

        self.p_construct_http_client = mock.patch.object(
            httpclient, '_construct_http_client')
        self.m_construct_http_client = self.p_construct_http_client.start()
        self.addCleanup(self.p_construct_http_client.stop)

    def run_cmd(self, cmd, formatting='json'):
        if formatting and formatting != 'table':
            formatter_arg = " -f %s" % formatting
            formatter = jsonutils.loads
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
