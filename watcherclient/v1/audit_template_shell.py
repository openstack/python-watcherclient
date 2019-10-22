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

import argparse

from osc_lib import utils
from oslo_utils import uuidutils

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
            '--goal',
            dest='goal',
            metavar='<goal>',
            help=_('UUID or name of the goal used for filtering.'))
        parser.add_argument(
            '--strategy',
            dest='strategy',
            metavar='<strategy>',
            help=_('UUID or name of the strategy used for filtering.'))
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
        parser.add_argument(
            '--marker',
            dest='marker',
            metavar='<marker>',
            default=None,
            help=_('UUID of the last audit template of the previous page; '
                   'displays list of audit templates after "marker".'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}

        # Optional
        if parsed_args.goal:
            params['goal'] = parsed_args.goal

        # Optional
        if parsed_args.strategy:
            params['strategy'] = parsed_args.strategy

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
        class SmartFormatter(argparse.HelpFormatter):

            def _split_lines(self, text, width):
                if '\n' in text:
                    return text.splitlines()
                else:
                    return argparse.HelpFormatter._split_lines(
                        self, text, width)

        parser = super(CreateAuditTemplate, self).get_parser(
            prog_name, formatter_class=SmartFormatter)
        parser.add_argument(
            'name',
            metavar='<name>',
            help=_('Name for this audit template.'))
        parser.add_argument(
            'goal',
            metavar='<goal>',
            help=_('Goal UUID or name associated to this audit template.'))
        parser.add_argument(
            '-s', '--strategy',
            dest='strategy',
            metavar='<strategy>',
            help=_('Strategy UUID or name associated to this audit template.'))
        parser.add_argument(
            '-d', '--description',
            metavar='<description>',
            help=_('Description of the audit template.'))
        parser.add_argument(
            '--scope',
            metavar='<path>',
            help=_("Part of the cluster on which an audit will be done.\n"
                   "Can be provided either in yaml or json file.\n"
                   "YAML example::\n"
                   "\n"
                   " - compute:\n"
                   "   - host_aggregates:\n"
                   "     - id: 1\n"
                   "     - id: 2\n"
                   "     - id: 3\n"
                   "   - availability_zones:\n"
                   "     - name: AZ1\n"
                   "     - name: AZ2\n"
                   "   - exclude:\n"
                   "     - instances:\n"
                   "       - uuid: UUID1\n"
                   "       - uuid: UUID2\n"
                   "     - compute_nodes:\n"
                   "       - name: compute1\n"
                   " - storage: \n"
                   "   - availability_zones:\n"
                   "     - name: AZ1\n"
                   "     - name: AZ2\n"
                   "   - volume_types:\n"
                   "     - name: lvm1\n"
                   "     - name: lvm2\n"
                   "   - exclude:\n"
                   "     - storage_pools:\n"
                   "       - name: host0@backend0#pool0\n"
                   "       - name: host1@backend1#pool1\n"
                   "     - volumes:\n"
                   "       - uuid: UUID1\n"
                   "       - uuid: UUID2\n"
                   "     - projects:\n"
                   "       - uuid: UUID1\n"
                   "       - uuid: UUID2\n"
                   "\n"
                   "JSON example::\n"
                   "\n"
                   " [\n"
                   "  {\"compute\":\n"
                   "       [{\"host_aggregates\": [\n"
                   "             {\"id\": 1},\n"
                   "             {\"id\": 2},\n"
                   "             {\"id\": 3}]},\n"
                   "        {\"availability_zones\": [\n"
                   "             {\"name\": \"AZ1\"},\n"
                   "             {\"name\": \"AZ2\"}]},\n"
                   "        {\"exclude\": [\n"
                   "             {\"instances\": [\n"
                   "                  {\"uuid\": \"UUID1\"},\n"
                   "                  {\"uuid\": \"UUID2\"}\n"
                   "             ]},\n"
                   "             {\"compute_nodes\": [\n"
                   "                  {\"name\": \"compute1\"}\n"
                   "             ]}\n"
                   "        ]}]\n"
                   "   },\n"
                   "  {\"storage\":\n"
                   "       [{\"availability_zones\": [\n"
                   "             {\"name\": \"AZ1\"},\n"
                   "             {\"name\": \"AZ2\"}]},\n"
                   "        {\"volume_types\": [\n"
                   "             {\"name\": \"lvm1\"},\n"
                   "             {\"name\": \"lvm2\"}]},\n"
                   "        {\"exclude\": [\n"
                   "             {\"storage_pools\": [\n"
                   "                  {\"name\": \"host0@backend0#pool0\"},\n"
                   "                  {\"name\": \"host1@backend1#pool1\"}\n"
                   "             ]},\n"
                   "             {\"volumes\": [\n"
                   "                  {\"uuid\": \"UUID1\"},\n"
                   "                  {\"uuid\": \"UUID2\"}\n"
                   "             ]},\n"
                   "             {\"projects\": [\n"
                   "                  {\"uuid\": \"UUID1\"},\n"
                   "                  {\"uuid\": \"UUID2\"}\n"
                   "             ]},\n"
                   "        ]}]\n"
                   "   }\n"
                   " ]\n"
                   )
        )

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        field_list = ['description', 'name', 'goal', 'strategy', 'scope']
        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)

        # mandatory
        if not uuidutils.is_uuid_like(fields['goal']):
            fields['goal'] = client.goal.get(fields['goal']).uuid

        # optional
        if fields.get('strategy'):
            if not uuidutils.is_uuid_like(fields['strategy']):
                fields['strategy'] = client.strategy.get(
                    fields['strategy']).uuid
        if fields.get('scope'):
            fields['scope'] = common_utils.serialize_file_to_dict(
                fields['scope'])

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
            help=_("Operation: 'add', 'replace', or 'remove'."))
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
