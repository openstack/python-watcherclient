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
from keystoneclient.auth.identity import v2
from keystoneclient.auth.identity import v3
from keystoneclient import discover
from keystoneclient import exceptions as ks_exc
from keystoneclient import session
from openstackclient.common import logs
from openstackclient.common import utils
import six.moves.urllib.parse as urlparse

from watcherclient._i18n import _
from watcherclient import exceptions as exc
from watcherclient import version

LOG = logging.getLogger(__name__)


API_NAME = 'infra-optim'
API_VERSIONS = {
    '1': 'watcherclient.v1.client.Client',
}
_DEFAULT_IDENTITY_API_VERSION = '3'
_IDENTITY_API_VERSION_2 = ['2', '2.0']
_IDENTITY_API_VERSION_3 = ['3']


class WatcherShell(app.App):
    """Watcher command line interface."""

    log = logging.getLogger(__name__)

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
        service_type = 'infra-optim'
        project_id = args.os_project_id or args.os_tenant_id
        project_name = args.os_project_name or args.os_tenant_name

        keystone_session = session.Session.load_from_cli_options(args)

        kwargs = {
            'username': args.os_username,
            'user_domain_id': args.os_user_domain_id,
            'user_domain_name': args.os_user_domain_name,
            'password': args.os_password,
            'auth_token': args.os_auth_token,
            'project_id': project_id,
            'project_name': project_name,
            'project_domain_id': args.os_project_domain_id,
            'project_domain_name': args.os_project_domain_name,
        }
        keystone_auth = self._get_keystone_auth(keystone_session,
                                                args.os_auth_url,
                                                **kwargs)
        region_name = args.os_region_name
        endpoint = keystone_auth.get_endpoint(keystone_session,
                                              service_type=service_type,
                                              region_name=region_name)

        endpoint_type = args.os_endpoint_type or 'publicURL'
        kwargs = {
            'auth_url': args.os_auth_url,
            'session': keystone_session,
            'auth': keystone_auth,
            'service_type': service_type,
            'endpoint_type': endpoint_type,
            'region_name': args.os_region_name,
            'username': args.os_username,
            'password': args.os_password,
        }

        watcher_client = utils.get_client_class(
            API_NAME,
            args.watcher_api_version or 1,
            API_VERSIONS)
        LOG.debug('Instantiating infra-optim client: %s', watcher_client)

        client = watcher_client(args.watcher_api_version, endpoint, **kwargs)

        return client

    def _discover_auth_versions(self, session, auth_url):
        # discover the API versions the server is supporting base on the
        # given URL
        v2_auth_url = None
        v3_auth_url = None
        try:
            ks_discover = discover.Discover(session=session, auth_url=auth_url)
            v2_auth_url = ks_discover.url_for('2.0')
            v3_auth_url = ks_discover.url_for('3.0')
        except ks_exc.ClientException:
            # Identity service may not support discover API version.
            # Let's try to figure out the API version from the original URL.
            url_parts = urlparse.urlparse(auth_url)
            (scheme, netloc, path, params, query, fragment) = url_parts
            path = path.lower()
            if path.startswith('/v3'):
                v3_auth_url = auth_url
            elif path.startswith('/v2'):
                v2_auth_url = auth_url
            else:
                # not enough information to determine the auth version
                msg = _('Unable to determine the Keystone version '
                        'to authenticate with using the given '
                        'auth_url. Identity service may not support API '
                        'version discovery. Please provide a versioned '
                        'auth_url instead. %s') % auth_url
                raise exc.CommandError(msg)

        return (v2_auth_url, v3_auth_url)

    def _get_keystone_v3_auth(self, v3_auth_url, **kwargs):
        auth_token = kwargs.pop('auth_token', None)
        if auth_token:
            return v3.Token(v3_auth_url, auth_token)
        else:
            return v3.Password(v3_auth_url, **kwargs)

    def _get_keystone_v2_auth(self, v2_auth_url, **kwargs):
        auth_token = kwargs.pop('auth_token', None)
        if auth_token:
            return v2.Token(
                v2_auth_url,
                auth_token,
                tenant_id=kwargs.pop('project_id', None),
                tenant_name=kwargs.pop('project_name', None))
        else:
            return v2.Password(
                v2_auth_url,
                username=kwargs.pop('username', None),
                password=kwargs.pop('password', None),
                tenant_id=kwargs.pop('project_id', None),
                tenant_name=kwargs.pop('project_name', None))

    def _get_keystone_auth(self, session, auth_url, **kwargs):
        # FIXME(dhu): this code should come from keystoneclient

        # discover the supported keystone versions using the given url
        (v2_auth_url, v3_auth_url) = self._discover_auth_versions(
            session=session,
            auth_url=auth_url)

        # Determine which authentication plugin to use. First inspect the
        # auth_url to see the supported version. If both v3 and v2 are
        # supported, then use the highest version if possible.
        auth = None
        if v3_auth_url and v2_auth_url:
            user_domain_name = kwargs.get('user_domain_name', None)
            user_domain_id = kwargs.get('user_domain_id', None)
            project_domain_name = kwargs.get('project_domain_name', None)
            project_domain_id = kwargs.get('project_domain_id', None)

            # support both v2 and v3 auth. Use v3 if domain information is
            # provided.
            if (user_domain_name or user_domain_id or project_domain_name or
                    project_domain_id):
                auth = self._get_keystone_v3_auth(v3_auth_url, **kwargs)
            else:
                auth = self._get_keystone_v2_auth(v2_auth_url, **kwargs)
        elif v3_auth_url:
            # support only v3
            auth = self._get_keystone_v3_auth(v3_auth_url, **kwargs)
        elif v2_auth_url:
            # support only v2
            auth = self._get_keystone_v2_auth(v2_auth_url, **kwargs)
        else:
            raise exc.CommandError(
                _('Unable to determine the Keystone version '
                  'to authenticate with using the given '
                  'auth_url.'))

        return auth

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
        parser.add_argument('--watcher-api-version',
                            metavar='<watcher-api-version>',
                            default=utils.env('WATCHER_API_VERSION'),
                            help='Defaults to env[WATCHER_API_VERSION].')
        parser.add_argument('--os-endpoint-type',
                            default=utils.env('OS_ENDPOINT_TYPE'),
                            help='Defaults to env[OS_ENDPOINT_TYPE] or '
                                 '"publicURL"')
        parser.epilog = ('See "watcher help COMMAND" for help '
                         'on a specific command.')
        session.Session.register_cli_options(parser)
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
            self.log.error('Exception raised: %s', str(e))

            return ret_val

        finally:
            self.log.info("END return value: %s", ret_val)


def main(argv=sys.argv[1:]):
    watcher_app = WatcherShell()
    return watcher_app.run(argv)

if __name__ == '__main__':   # pragma: no cover
    sys.exit(main(sys.argv[1:]))
