# -*- coding: utf-8 -*-
#
# Copyright 2015 b<>com
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.


# Audit Template
AUDIT_TEMPLATE_FIELDS = [
    'uuid', 'created_at', 'updated_at', 'deleted_at',
    'description', 'host_aggregate', 'name',
    'extra', 'goal']

AUDIT_TEMPLATE_FIELD_LABELS = [
    'UUID', 'Created At', 'Updated At', 'Deleted At',
    'Description', 'Host Aggregate ID or Name', 'Name',
    'Extra', 'Goal Type']

AUDIT_TEMPLATE_SHORT_LIST_FIELDS = ['uuid', 'name']

AUDIT_TEMPLATE_SHORT_LIST_FIELD_LABELS = ['UUID', 'Name']

# Audit
AUDIT_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                'deadline', 'state', 'type', 'audit_template_uuid',
                'audit_template_name']

AUDIT_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                      'Deadline', 'State', 'Type', 'Audit Template uuid',
                      'Audit Template Name']

AUDIT_SHORT_LIST_FIELDS = ['uuid', 'type', 'audit_template_name', 'state']

AUDIT_SHORT_LIST_FIELD_LABELS = ['UUID', 'Type', 'Audit Template Name',
                                 'State']

# Action Plan
ACTION_PLAN_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                      'audit_uuid', 'state']

ACTION_PLAN_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                            'Audit', 'State']

ACTION_PLAN_SHORT_LIST_FIELDS = ['uuid', 'audit_uuid', 'state', 'updated_at']

ACTION_PLAN_SHORT_LIST_FIELD_LABELS = ['UUID', 'Audit', 'State', 'Updated At']

# Action
ACTION_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at', 'next_uuid',
                 'description', 'alarm', 'state', 'action_plan_uuid',
                 'action_type', 'applies_to', 'src', 'dst', 'parameter']

ACTION_FIELD_LABELS = ['UUID', 'Created At', 'Updated At', 'Deleted At',
                       'Next Action', 'Description', 'Alarm', 'State',
                       'Action Plan', 'Action',
                       'Applies to', 'Hypervisor Source',
                       'Hypervisor Destination', 'Parameter']

ACTION_SHORT_LIST_FIELDS = ['uuid', 'next_uuid',
                            'state', 'action_plan_uuid', 'action_type']

ACTION_SHORT_LIST_FIELD_LABELS = ['UUID', 'Next Action', 'State',
                                  'Action Plan', 'Action']
# Goals

GOAL_FIELDS = ['name', 'strategy']

GOAL_FIELD_LABELS = ['Name', 'Strategy']

GOAL_SHORT_LIST_FIELDS = ['name', 'strategy']

GOAL_SHORT_LIST_FIELD_LABELS = ['Name', 'Strategy']

# Metric Collector
METRIC_COLLECTOR_FIELDS = ['uuid', 'created_at', 'updated_at', 'deleted_at',
                           'endpoint', 'category']

METRIC_COLLECTOR_FIELD_LABELS = ['UUID', 'Created At', 'Updated At',
                                 'Deleted At', 'Endpoint URL',
                                 'Metric Category']

METRIC_COLLECTOR_SHORT_LIST_FIELDS = ['uuid', 'endpoint', 'category']

METRIC_COLLECTOR_SHORT_LIST_FIELD_LABELS = ['UUID', 'Endpoint URL',
                                            'Metric Category']
