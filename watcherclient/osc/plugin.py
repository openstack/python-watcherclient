#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.


import logging

from osc_lib import utils

import watcherclient
from watcherclient.common import api_versioning
from watcherclient.common import httpclient
from watcherclient import exceptions

LOG = logging.getLogger(__name__)

DEFAULT_API_VERSION = httpclient.LATEST_VERSION
API_VERSION_OPTION = 'os_infra_optim_api_version'
API_NAME = 'infra-optim'
API_VERSIONS = {
    '1': 'watcherclient.v1.client.Client',
}


def make_client(instance):
    """Returns an infra-optim service client."""

    version = api_versioning.APIVersion(instance._api_version[API_NAME])

    infraoptim_client_class = utils.get_client_class(
        API_NAME,
        version.ver_major,
        API_VERSIONS)
    LOG.debug('Instantiating infraoptim client: %s', infraoptim_client_class)

    client = infraoptim_client_class(
        os_infra_optim_api_version=instance._api_version[API_NAME],
        session=instance.session,
        region_name=instance._region_name,
    )

    return client


def build_option_parser(parser):
    """Hook to add global options."""
    parser.add_argument('--os-infra-optim-api-version',
                        metavar='<infra-optim-api-version>',
                        default=utils.env(
                            'OS_INFRA_OPTIM_API_VERSION',
                            default=DEFAULT_API_VERSION),
                        help=('Watcher API version, default=' +
                              DEFAULT_API_VERSION +
                              ' (Env: OS_INFRA_OPTIM_API_VERSION)'))
    return parser


def check_api_version(check_version):
    """Validate version supplied by user

    Returns:
    * True if version is OK
    * False if the version has not been checked and the previous plugin
    check should be performed
    * throws an exception if the version is no good
    """

    infra_api_version = api_versioning.get_api_version(check_version)

    # Bypass X.latest format microversion
    if not infra_api_version.is_latest():
        if infra_api_version > api_versioning.APIVersion("2.0"):
            if not infra_api_version.matches(
                watcherclient.API_MIN_VERSION,
                watcherclient.API_MAX_VERSION,
            ):
                msg = "versions supported by client: %(min)s - %(max)s" % {
                    "min": watcherclient.API_MIN_VERSION.get_string(),
                    "max": watcherclient.API_MAX_VERSION.get_string(),
                }
                raise exceptions.CommandError(msg)
    return True
