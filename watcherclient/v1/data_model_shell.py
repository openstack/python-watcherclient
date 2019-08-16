# Copyright 2019 ZTE Corporation.
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
from watcherclient._i18n import _
from watcherclient.common import command
from watcherclient import exceptions
from watcherclient.v1 import resource_fields as res_fields


class ListDataModel(command.Lister):
    """List information on retrieved data model."""

    def get_parser(self, prog_name):
        parser = super(ListDataModel, self).get_parser(prog_name)
        parser.add_argument(
            '--type',
            metavar='<type>',
            dest='type',
            help=_('Type of Datamodel user want to list. '
                   'Supported values: compute. '
                   'Future support values: storage, baremetal. '
                   'Default type is compute.'))
        parser.add_argument(
            '--audit',
            metavar='<audit>',
            dest='audit',
            help=_('UUID of the audit'))
        parser.add_argument(
            '--detail',
            dest='detail',
            action='store_true',
            default=False,
            help=_("Show detailed information about data model."))
        return parser

    def get_tuple(self, dic, fields):
        ret_tup = []
        for item in fields:
            ret_tup.append(dic.get(item))
        return tuple(ret_tup)

    def take_action(self, parsed_args):
        client = getattr(self.app.client_manager, "infra-optim")
        allowed_type = ['compute', 'storage', 'baremetal']
        params = {}
        if parsed_args.audit:
            params["audit"] = parsed_args.audit
        if parsed_args.type:
            if parsed_args.type not in allowed_type:
                raise exceptions.CommandError(
                    'Type %s error, '
                    'Please check the valid type!' % parsed_args.type)
            params["data_model_type"] = parsed_args.type
        try:
            data_model = client.data_model.list(**params)
        except exceptions.HTTPNotFound as exc:
            raise exceptions.CommandError(str(exc))
        # TODO(chenker) Add Storage MODEL_FIELDS when using Storage Datamodel.
        if parsed_args.detail:
            fields = res_fields.COMPUTE_MODEL_LIST_FIELDS
            field_labels = res_fields.COMPUTE_MODEL_LIST_FIELD_LABELS
        else:
            fields = res_fields.COMPUTE_MODEL_SHORT_LIST_FIELDS
            field_labels = res_fields.COMPUTE_MODEL_SHORT_LIST_FIELD_LABELS
        return (field_labels,
                (self.get_tuple(item, fields) for item in data_model.context))
