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
from oslo_utils import uuidutils

from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient.common import utils as common_utils
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


class ShowAudit(command.ShowOne):
    """Show detailed information about a given audit."""

    def get_parser(self, prog_name):
        parser = super(ShowAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audit',
            metavar='<audit>',
            help=_('UUID of the audit'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        try:
            audit = client.audit.get(parsed_args.audit)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS

        return column_headers, utils.get_item_properties(audit, columns)


class ListAudit(command.Lister):
    """List information on retrieved audits."""

    def get_parser(self, prog_name):
        parser = super(ListAudit, self).get_parser(prog_name)
        parser.add_argument(
            '--audit-template',
            metavar='<audit_template>',
            dest='audit_template',
            help=_('Name or UUID of an audit template used for filtering.'))
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about audits."))
        parser.add_argument(
            '--limit',
            metavar='<limit>',
            type=int,
            help=_('Maximum number of audits to return per request, '
                   '0 for no limit. Default is the maximum number used '
                   'by the Watcher API Service.'))
        parser.add_argument(
            '--sort-key',
            metavar='<field>',
            help=_('Audit field that will be used for sorting.'))
        parser.add_argument(
            '--sort-dir',
            metavar='<direction>',
            choices=['asc', 'desc'],
            help=_('Sort direction: "asc" (the default) or "desc".'))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        params = {}
        if parsed_args.audit_template is not None:
            params['audit_template'] = parsed_args.audit_template
        if parsed_args.detail:
            fields = res_fields.AUDIT_FIELDS
            field_labels = res_fields.AUDIT_FIELD_LABELS
        else:
            fields = res_fields.AUDIT_SHORT_LIST_FIELDS
            field_labels = res_fields.AUDIT_SHORT_LIST_FIELD_LABELS

        params.update(common_utils.common_params_for_list(
            parsed_args, fields, field_labels))

        try:
            data = client.audit.list(**params)
        except exceptions.HTTPNotFound as ex:
            raise exceptions.CommandError(str(ex))

        return (field_labels,
                (utils.get_item_properties(item, fields) for item in data))


class CreateAudit(command.ShowOne):
    """Create new audit."""

    def get_parser(self, prog_name):
        parser = super(CreateAudit, self).get_parser(prog_name)
        parser.add_argument(
            '-a', '--audit-template',
            required=True,
            dest='audit_template_uuid',
            metavar='<audit_template>',
            help=_('Audit template used for this audit (name or uuid).'))
        parser.add_argument(
            '-d', '--deadline',
            dest='deadline',
            metavar='<deadline>',
            help=_('Descrition of the audit.'))
        parser.add_argument(
            '-t', '--audit_type',
            dest='audit_type',
            metavar='<audit_type>',
            default='ONESHOT',
            help=_("Audit type."))
        parser.add_argument(
            '-p', '--parameter',
            dest='parameters',
            metavar='<name=value>',
            action='append',
            help=_("Record strategy parameter/value metadata. "
                   "Can be specified multiple times."))
        parser.add_argument(
            '-i', '--interval',
            dest='interval',
            metavar='<interval>',
            help=_("Audit interval."))

        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        field_list = ['audit_template_uuid', 'audit_type',
                      'deadline', 'parameters', 'interval']

        fields = dict((k, v) for (k, v) in vars(parsed_args).items()
                      if k in field_list and v is not None)
        fields = common_utils.args_array_to_dict(fields, 'parameters')
        if fields.get('audit_template_uuid'):
            if not uuidutils.is_uuid_like(fields['audit_template_uuid']):
                fields['audit_template_uuid'] = client.audit_template.get(
                    fields['audit_template_uuid']).uuid

        audit = client.audit.create(**fields)

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS

        return column_headers, utils.get_item_properties(audit, columns)


class UpdateAudit(command.ShowOne):
    """Update audit command."""

    def get_parser(self, prog_name):
        parser = super(UpdateAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audit',
            metavar='<audit>',
            help=_("UUID of the audit."))
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

        if not uuidutils.is_uuid_like(parsed_args.audit):
            raise exceptions.ValidationError()

        patch = common_utils.args_array_to_patch(
            parsed_args.op, parsed_args.attributes[0])

        audit = client.audit.update(parsed_args.audit, patch)

        columns = res_fields.AUDIT_FIELDS
        column_headers = res_fields.AUDIT_FIELD_LABELS

        return column_headers, utils.get_item_properties(audit, columns)


class DeleteAudit(command.Command):
    """Delete audit command."""

    def get_parser(self, prog_name):
        parser = super(DeleteAudit, self).get_parser(prog_name)
        parser.add_argument(
            'audits',
            metavar='<audit>',
            nargs='+',
            help=_('UUID of the audit'),
        )
        return parser

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")

        for audit in parsed_args.audits:
            if not uuidutils.is_uuid_like(audit):
                raise exceptions.ValidationError()

            client.audit.delete(audit)
