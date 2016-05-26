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
from openstackclient.common import utils

from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


class ShowStrategy(command.ShowOne):
    """Show detailed information about a given strategy."""

    def get_parser(self, prog_name):
        parser = super(ShowStrategy, self).get_parser(prog_name)
        parser.add_argument(
            'strategy',
            metavar='<strategy>',
            help=_('UUID or name of the strategy'),
        )
        return parser

    def _format_spec(self, strategy):
        parameters_spec = strategy.parameters_spec.get('properties')
        if parameters_spec:
            return json.dumps(parameters_spec, indent=2)

        return {}

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        try:
            strategy = client.strategy.get(parsed_args.strategy)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        strategy.parameters_spec = self._format_spec(strategy)
        columns = res_fields.STRATEGY_FIELDS
        column_headers = res_fields.STRATEGY_FIELD_LABELS

        return column_headers, utils.get_item_properties(strategy, columns)


class ListStrategy(command.Lister):
    """List information on retrieved strategies."""

    def get_parser(self, prog_name):
        parser = super(ListStrategy, self).get_parser(prog_name)
        parser.add_argument(
            '--goal',
            metavar='<goal>',
            dest='goal',
            help=_('UUID or name of the goal'))
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about each strategy."))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of strategies to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Goal field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help='Sort direction: "asc" (the default) or "desc".')

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}
        if parsed_args.detail:
            fields = res_fields.STRATEGY_FIELDS
            field_labels = res_fields.STRATEGY_FIELD_LABELS
        else:
            fields = res_fields.STRATEGY_SHORT_LIST_FIELDS
            field_labels = res_fields.STRATEGY_SHORT_LIST_FIELD_LABELS

        if parsed_args.goal:
            params["goal"] = parsed_args.goal

        params.update(
            common_utils.common_params_for_list(
                parsed_args, fields, field_labels))

        try:
            data = client.strategy.list(**params)
        except exceptions.HTTPNotFound as ex:
            raise exceptions.CommandError(str(ex))

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))
