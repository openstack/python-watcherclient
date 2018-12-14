# Copyright (c) 2013 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Command-line interface to the Watcher API.
"""
from collections import namedtuple
import logging
import sys

from cliff import app
from cliff import command
from cliff import commandmanager
from cliff import complete
from cliff import help as cli_help
from keystoneauth1 import loading
from osc_lib import logs
from osc_lib import utils

from watcherclient import client as watcherclient
from watcherclient import version

LOG = logging.getLogger(__name__)


API_NAME = 'infra-optim'
API_VERSIONS = {
    '1': 'watcherclient.v1.client.Client',
}
DEFAULT_OS_INFRA_OPTIM_API_VERSION = '1.latest'
_DEFAULT_IDENTITY_API_VERSION = '3'
_IDENTITY_API_VERSION_2 = ['2', '2.0']
_IDENTITY_API_VERSION_3 = ['3']


class WatcherShell(app.App):
    """Watcher command line interface."""

    def __init__(self, **kwargs):
        self.client = None

        # Patch command.Command to add a default auth_required = True
        command.Command.auth_required = True

        # Some commands do not need authentication
        cli_help.HelpCommand.auth_required = False
        complete.CompleteCommand.auth_required = False

        super(WatcherShell, self).__init__(
            description=__doc__.strip(),
            version=version.__version__,
            command_manager=commandmanager.CommandManager(
                'watcherclient.v1'),
            deferred_help=True,
            **kwargs
        )

    def create_client(self, args):
        client = watcherclient.get_client('1', **args.__dict__)
        return client

    def build_option_parser(self, description, version, argparse_kwargs=None):
        """Introduces global arguments for the application.

        This is inherited from the framework.
        """
        parser = super(WatcherShell, self).build_option_parser(
            description, version, argparse_kwargs)
        parser.add_argument('--no-auth', '-N', action='store_true',
                            help='Do not use authentication.')
        parser.add_argument('--os-identity-api-version',
                            metavar='<identity-api-version>',
                            default=utils.env('OS_IDENTITY_API_VERSION'),
                            help='Specify Identity API version to use. '
                            'Defaults to env[OS_IDENTITY_API_VERSION]'
                            ' or 3.')
        parser.add_argument('--os-auth-url', '-A',
                            metavar='<auth-url>',
                            default=utils.env('OS_AUTH_URL'),
                            help='Defaults to env[OS_AUTH_URL].')
        parser.add_argument('--os-region-name', '-R',
                            metavar='<region-name>',
                            default=utils.env('OS_REGION_NAME'),
                            help='Defaults to env[OS_REGION_NAME].')
        parser.add_argument('--os-username', '-U',
                            metavar='<auth-user-name>',
                            default=utils.env('OS_USERNAME'),
                            help='Defaults to env[OS_USERNAME].')
        parser.add_argument('--os-user-id',
                            metavar='<auth-user-id>',
                            default=utils.env('OS_USER_ID'),
                            help='Defaults to env[OS_USER_ID].')
        parser.add_argument('--os-password', '-P',
                            metavar='<auth-password>',
                            default=utils.env('OS_PASSWORD'),
                            help='Defaults to env[OS_PASSWORD].')
        parser.add_argument('--os-user-domain-id',
                            metavar='<auth-user-domain-id>',
                            default=utils.env('OS_USER_DOMAIN_ID'),
                            help='Defaults to env[OS_USER_DOMAIN_ID].')
        parser.add_argument('--os-user-domain-name',
                            metavar='<auth-user-domain-name>',
                            default=utils.env('OS_USER_DOMAIN_NAME'),
                            help='Defaults to env[OS_USER_DOMAIN_NAME].')
        parser.add_argument('--os-tenant-name', '-T',
                            metavar='<auth-tenant-name>',
                            default=utils.env('OS_TENANT_NAME'),
                            help='Defaults to env[OS_TENANT_NAME].')
        parser.add_argument('--os-tenant-id', '-I',
                            metavar='<tenant-id>',
                            default=utils.env('OS_TENANT_ID'),
                            help='Defaults to env[OS_TENANT_ID].')
        parser.add_argument('--os-project-id',
                            metavar='<auth-project-id>',
                            default=utils.env('OS_PROJECT_ID'),
                            help='Another way to specify tenant ID. '
                                 'This option is mutually exclusive with '
                                 ' --os-tenant-id. '
                            'Defaults to env[OS_PROJECT_ID].')
        parser.add_argument('--os-project-name',
                            metavar='<auth-project-name>',
                            default=utils.env('OS_PROJECT_NAME'),
                            help='Another way to specify tenant name. '
                                 'This option is mutually exclusive with '
                                 ' --os-tenant-name. '
                                 'Defaults to env[OS_PROJECT_NAME].')
        parser.add_argument('--os-project-domain-id',
                            metavar='<auth-project-domain-id>',
                            default=utils.env('OS_PROJECT_DOMAIN_ID'),
                            help='Defaults to env[OS_PROJECT_DOMAIN_ID].')
        parser.add_argument('--os-project-domain-name',
                            metavar='<auth-project-domain-name>',
                            default=utils.env('OS_PROJECT_DOMAIN_NAME'),
                            help='Defaults to env[OS_PROJECT_DOMAIN_NAME].')
        parser.add_argument('--os-auth-token',
                            metavar='<auth-token>',
                            default=utils.env('OS_AUTH_TOKEN'),
                            help='Defaults to env[OS_AUTH_TOKEN].')
        parser.add_argument(
            '--os-infra-optim-api-version',
            metavar='<infra-optim-api-version>',
            default=utils.env('OS_INFRA_OPTIM_API_VERSION',
                              default=DEFAULT_OS_INFRA_OPTIM_API_VERSION),
            help='Accepts X, X.Y (where X is major and Y is minor part) or '
                 '"X.latest", defaults to env[OS_INFRA_OPTIM_API_VERSION].')
        parser.add_argument('--os-endpoint-type',
                            default=utils.env('OS_ENDPOINT_TYPE'),
                            help='Defaults to env[OS_ENDPOINT_TYPE] or '
                                 '"publicURL"')
        parser.add_argument('--os-endpoint-override',
                            metavar='<endpoint-override>',
                            default=utils.env('OS_ENDPOINT_OVERRIDE'),
                            help="Use this API endpoint instead of the "
                                 "Service Catalog.")
        parser.epilog = ('See "watcher help COMMAND" for help '
                         'on a specific command.')
        loading.register_session_argparse_arguments(parser)
        return parser

    def configure_logging(self):
        """Configure logging for the app."""
        self.log_configurator = logs.LogConfigurator(self.options)
        self.dump_stack_trace = self.log_configurator.dump_trace

    def prepare_to_run_command(self, cmd):
        """Prepares to run the command

        Checks if the minimal parameters are provided and creates the
        client interface.
        This is inherited from the framework.
        """
        self.client_manager = namedtuple('ClientManager', 'infra_optim')
        if cmd.auth_required:
            client = self.create_client(self.options)
            setattr(self.client_manager, 'infra-optim', client)

    def run(self, argv):
        ret_val = 1
        self.command_options = argv
        try:
            ret_val = super(WatcherShell, self).run(argv)
            return ret_val
        except Exception as e:
            if not logging.getLogger('').handlers:
                logging.basicConfig()
            LOG.error('Exception raised: %s', str(e))

            return ret_val

        finally:
            LOG.info("END return value: %s", ret_val)


def main(argv=sys.argv[1:]):
    watcher_app = WatcherShell()
    return watcher_app.run(argv)


if __name__ == '__main__':   # pragma: no cover
    sys.exit(main(sys.argv[1:]))
