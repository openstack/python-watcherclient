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

from openstackclient.common import utils

from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


class ShowAuditTemplate(command.ShowOne):
    """Show detailed information about a given audit template."""

    def get_parser(self, prog_name):
        parser = super(ShowAuditTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'audit_template',
            metavar='<audit-template>',
            help=_('UUID or name of the audit template'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        audit_template_uuid = parsed_args.audit_template

        try:
            audit_template = client.audit_template.get(audit_template_uuid)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        columns = res_fields.AUDIT_TEMPLATE_FIELDS
        column_headers = res_fields.AUDIT_TEMPLATE_FIELD_LABELS

        return column_headers, utils.get_item_properties(
            audit_template, columns)


class ListAuditTemplate(command.Lister):
    """List information on retrieved audit templates."""

    def get_parser(self, prog_name):
        parser = super(ListAuditTemplate, self).get_parser(prog_name)
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about audit templates."))
        parser.add_argument(
            '--goal-uuid',
            metavar='<goal-uuid>',
            help=_('UUID the goal used for filtering.'))
        parser.add_argument(
            '--strategy-uuid',
            metavar='<strategy-uuid>',
            help=_('UUID the strategy used for filtering.'))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of audit templates to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Audit template field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help=_('Sort direction: "asc" (the default) or "desc".'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}

        if parsed_args.goal_uuid is not None:
            params['goal_uuid'] = parsed_args.goal_uuid
        if parsed_args.strategy_uuid is not None:
            params['strategy_uuid'] = parsed_args.strategy_uuid
        if parsed_args.detail:
            fields = res_fields.AUDIT_TEMPLATE_FIELDS
            field_labels = res_fields.AUDIT_TEMPLATE_FIELD_LABELS
        else:
            fields = res_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELDS
            field_labels = res_fields.AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS

        params.update(common_utils.common_params_for_list(
            parsed_args, fields, field_labels))

        data = client.audit_template.list(**params)

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))


class CreateAuditTemplate(command.ShowOne):
    """Create new audit template."""

    def get_parser(self, prog_name):
        parser = super(CreateAuditTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name for this audit template.'))
        parser.add_argument(
            'goal_uuid',
            metavar='<goal-uuid>',
            help=_('Goal ID associated to this audit template.'))
        parser.add_argument(
            '-s', '--strategy-uuid',
            dest='strategy_uuid',
            metavar='<strategy-uuid>',
            help=_('Strategy ID associated to this audit template.'))
        parser.add_argument(
            '-d', '--description',
            metavar='<description>',
            help=_('Descrition of the audit template.'))
        parser.add_argument(
            '-e', '--extra',
            metavar='<key=value>',
            action='append',
            help=_("Record arbitrary key/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '-a', '--host-aggregate',
            dest='host_aggregate',
            metavar='<host-aggregate>',
            help=_('Name or UUID of the host aggregate targeted '
                   'by this audit template.'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        field_list = ['host_aggregate', 'description', 'name', 'extra',
                      'goal_uuid', 'strategy_uuid']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = common_utils.args_array_to_dict(fields, 'extra')
        audit_template = client.audit_template.create(**fields)

        columns = res_fields.AUDIT_TEMPLATE_FIELDS
        column_headers = res_fields.AUDIT_TEMPLATE_FIELD_LABELS

        return (column_headers,
                utils.get_item_properties(audit_template, columns))


class UpdateAuditTemplate(command.ShowOne):
    """Update audit template command."""

    def get_parser(self, prog_name):
        parser = super(UpdateAuditTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'audit_template',
            metavar='<audit-template>',
            help=_("UUID or name of the audit_template."))
        parser.add_argument(
            'op',
            metavar='<op>',
            choices=['add', 'replace', 'remove'],
            help=_("Operation: 'add'), 'replace', or 'remove'."))
        parser.add_argument(
            'attributes',
            metavar='<path=value>',
            nargs='+',
            action='append',
            default=[],
            help=_("Attribute to add, replace, or remove. Can be specified "
                   "multiple times. For 'remove', only <path> is necessary."))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        patch = common_utils.args_array_to_patch(
            parsed_args.op, parsed_args.attributes[0])

        audit_template = client.audit_template.update(
            parsed_args.audit_template, patch)

        columns = res_fields.AUDIT_TEMPLATE_FIELDS
        column_headers = res_fields.AUDIT_TEMPLATE_FIELD_LABELS

        return column_headers, utils.get_item_properties(
            audit_template, columns)


class DeleteAuditTemplate(command.Command):
    """Delete audit template command."""

    def get_parser(self, prog_name):
        parser = super(DeleteAuditTemplate, self).get_parser(prog_name)
        parser.add_argument(
            'audit_templates',
            metavar='<audit-template>',
            nargs='+',
            help=_('UUID or name of the audit template'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        for audit_template in parsed_args.audit_templates:
            client.audit_template.delete(audit_template)
