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

from watcherclient.v1 import action
from watcherclient.v1 import action_plan
from watcherclient.v1 import audit
from watcherclient.v1 import audit_template
from watcherclient.v1 import goal
from watcherclient.v1 import strategy

Action = action.Action
ActionManager = action.ActionManager
ActionPlan = action_plan.ActionPlan
ActionPlanManager = action_plan.ActionPlanManager
Audit = audit.Audit
AuditManager = audit.AuditManager
AuditTemplate = audit_template.AuditTemplate
AuditTemplateManager = audit_template.AuditTemplateManager
Goal = goal.Goal
GoalManager = goal.GoalManager
Strategy = strategy.Strategy
StrategyManager = strategy.StrategyManager

__all__ = (
    "Action", "ActionManager", "ActionPlan", "ActionPlanManager",
    "Audit", "AuditManager", "AuditTemplate", "AuditTemplateManager",
    "Goal", "GoalManager", "Strategy", "StrategyManager")
