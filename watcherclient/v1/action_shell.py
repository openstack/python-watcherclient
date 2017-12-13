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

from osc_lib import utils

from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


class ShowAction(command.ShowOne):
    """Show detailed information about a given action."""

    def get_parser(self, prog_name):
        parser = super(ShowAction, self).get_parser(prog_name)
        parser.add_argument(
            'action',
            metavar='<action>',
            help=_('UUID of the action'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        try:
            action = client.action.get(parsed_args.action)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        columns = res_fields.ACTION_FIELDS
        column_headers = res_fields.ACTION_FIELD_LABELS

        return column_headers, utils.get_item_properties(action, columns)


class ListAction(command.Lister):
    """List information on retrieved actions."""

    def get_parser(self, prog_name):
        parser = super(ListAction, self).get_parser(prog_name)
        parser.add_argument(
            '--action-plan',
            metavar='<action-plan>',
            help=_('UUID of the action plan used for filtering.'))
        parser.add_argument(
            '--audit',
            metavar='<audit>',
            help=_(' UUID of the audit used for filtering.'))
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about actions."))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of actions to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Action field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help=_('Sort direction: "asc" (the default) or "desc".'))
        parser.add_argument(
            '--marker',
            dest='marker',
            metavar='<marker>',
            default=None,
            help=_('UUID of the last action in the previous page; '
                   'displays list of actions after "marker".'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}
        if parsed_args.action_plan is not None:
            params['action_plan'] = parsed_args.action_plan
        if parsed_args.audit is not None:
            params['audit'] = parsed_args.audit
        if parsed_args.detail:
            fields = res_fields.ACTION_FIELDS
            field_labels = res_fields.ACTION_FIELD_LABELS
        else:
            fields = res_fields.ACTION_SHORT_LIST_FIELDS
            field_labels = res_fields.ACTION_SHORT_LIST_FIELD_LABELS

        params.update(
            common_utils.common_params_for_list(
                parsed_args, fields, field_labels))

        try:
            data = client.action.list(**params)
        except exceptions.HTTPNotFound as ex:
            raise exceptions.CommandError(str(ex))

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))
