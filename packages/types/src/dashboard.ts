/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { EDurationFilters } from "./enums";
import type { IIssueActivity, TIssuePriorities } from "./issues";
import type { TIssue } from "./issues/issue";
import type { TIssueRelationTypes } from "./issues/issue_relation";
import type { TStateGroups } from "./state";

export type TWidgetKeys =
  | "overview_stats"
  | "assigned_issues"
  | "created_issues"
  | "issues_by_state_groups"
  | "issues_by_priority"
  | "recent_activity"
  | "recent_projects"
  | "recent_collaborators"
  | "issues_by_status"
  | "assignee_workload"
  | "issues_trend"
  | "cycle_burndown"
  | "velocity"
  | "lead_time"
  | "cycle_time"
  | "cumulative_flow";

export type TIssuesListTypes = "pending" | "upcoming" | "overdue" | "completed";

// widget filters
export type TAssignedIssuesWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  tab?: TIssuesListTypes;
};

export type TCreatedIssuesWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  tab?: TIssuesListTypes;
};

export type TIssuesByStateGroupsWidgetFilters = {
  duration?: EDurationFilters;
  custom_dates?: string[];
};

export type TIssuesByPriorityWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
};

export type TIssuesByStatusWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
};

export type TAssigneeWorkloadWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
  assignees?: string[];
};

export type TIssuesTrendWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
  segment_by?: "state_group" | "priority" | "assignee";
};

export type TCycleBurndownWidgetFilters = {
  cycle_id?: string;
  project_ids?: string[];
  plot_type?: "burndown" | "burnup";
};

export type TVelocityWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
  segment_by?: "week" | "month";
};

export type TLeadTimeWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
};

export type TCycleTimeWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
};

export type TCumulativeFlowWidgetFilters = {
  custom_dates?: string[];
  duration?: EDurationFilters;
  project_ids?: string[];
};

export type TWidgetFiltersFormData =
  | {
      widgetKey: "assigned_issues";
      filters: Partial<TAssignedIssuesWidgetFilters>;
    }
  | {
      widgetKey: "created_issues";
      filters: Partial<TCreatedIssuesWidgetFilters>;
    }
  | {
      widgetKey: "issues_by_state_groups";
      filters: Partial<TIssuesByStateGroupsWidgetFilters>;
    }
  | {
      widgetKey: "issues_by_priority";
      filters: Partial<TIssuesByPriorityWidgetFilters>;
    }
  | {
      widgetKey: "issues_by_status";
      filters: Partial<TIssuesByStatusWidgetFilters>;
    }
  | {
      widgetKey: "assignee_workload";
      filters: Partial<TAssigneeWorkloadWidgetFilters>;
    }
  | {
      widgetKey: "issues_trend";
      filters: Partial<TIssuesTrendWidgetFilters>;
    }
  | {
      widgetKey: "cycle_burndown";
      filters: Partial<TCycleBurndownWidgetFilters>;
    }
  | {
      widgetKey: "velocity";
      filters: Partial<TVelocityWidgetFilters>;
    }
  | {
      widgetKey: "lead_time";
      filters: Partial<TLeadTimeWidgetFilters>;
    }
  | {
      widgetKey: "cycle_time";
      filters: Partial<TCycleTimeWidgetFilters>;
    }
  | {
      widgetKey: "cumulative_flow";
      filters: Partial<TCumulativeFlowWidgetFilters>;
    };

export type TWidget = {
  id: string;
  is_visible: boolean;
  key: TWidgetKeys;
  readonly widget_filters: // only for read
  TAssignedIssuesWidgetFilters &
    TCreatedIssuesWidgetFilters &
    TIssuesByStateGroupsWidgetFilters &
    TIssuesByPriorityWidgetFilters &
    TIssuesByStatusWidgetFilters &
    TAssigneeWorkloadWidgetFilters &
    TIssuesTrendWidgetFilters &
    TCycleBurndownWidgetFilters &
    TVelocityWidgetFilters &
    TLeadTimeWidgetFilters &
    TCycleTimeWidgetFilters &
    TCumulativeFlowWidgetFilters;
  filters: // only for write
  TAssignedIssuesWidgetFilters &
    TCreatedIssuesWidgetFilters &
    TIssuesByStateGroupsWidgetFilters &
    TIssuesByPriorityWidgetFilters &
    TIssuesByStatusWidgetFilters &
    TAssigneeWorkloadWidgetFilters &
    TIssuesTrendWidgetFilters &
    TCycleBurndownWidgetFilters &
    TVelocityWidgetFilters &
    TLeadTimeWidgetFilters &
    TCycleTimeWidgetFilters &
    TCumulativeFlowWidgetFilters;
};

export type TWidgetStatsRequestParams =
  | {
      widget_key: TWidgetKeys;
    }
  | {
      target_date: string;
      issue_type: TIssuesListTypes;
      widget_key: "assigned_issues";
      expand?: "issue_relation";
    }
  | {
      target_date: string;
      issue_type: TIssuesListTypes;
      widget_key: "created_issues";
    }
  | {
      target_date: string;
      widget_key: "issues_by_state_groups";
    }
  | {
      target_date: string;
      widget_key: "issues_by_priority";
    }
  | {
      cursor: string;
      per_page: number;
      search?: string;
      widget_key: "recent_collaborators";
    }
  | {
      target_date: string;
      widget_key: "issues_by_status";
      project_ids?: string[];
    }
  | {
      target_date: string;
      widget_key: "assignee_workload";
      project_ids?: string[];
      assignees?: string[];
    }
  | {
      target_date: string;
      widget_key: "issues_trend";
      project_ids?: string[];
      segment_by?: "state_group" | "priority" | "assignee";
    }
  | {
      target_date: string;
      widget_key: "cycle_burndown";
      cycle_id: string;
      project_ids?: string[];
      plot_type?: "burndown" | "burnup";
    }
  | {
      target_date: string;
      widget_key: "velocity";
      project_ids?: string[];
      segment_by?: "week" | "month";
    }
  | {
      target_date: string;
      widget_key: "lead_time";
      project_ids?: string[];
    }
  | {
      target_date: string;
      widget_key: "cycle_time";
      project_ids?: string[];
    }
  | {
      target_date: string;
      widget_key: "cumulative_flow";
      project_ids?: string[];
    };

export type TWidgetIssue = TIssue & {
  issue_relation: {
    id: string;
    project_id: string;
    relation_type: TIssueRelationTypes;
    sequence_id: number;
    type_id: string | null;
  }[];
};

// widget stats responses
export type TOverviewStatsWidgetResponse = {
  assigned_issues_count: number;
  completed_issues_count: number;
  created_issues_count: number;
  pending_issues_count: number;
};

export type TAssignedIssuesWidgetResponse = {
  issues: TWidgetIssue[];
  count: number;
};

export type TCreatedIssuesWidgetResponse = {
  issues: TWidgetIssue[];
  count: number;
};

export type TIssuesByStateGroupsWidgetResponse = {
  count: number;
  state: TStateGroups;
};

export type TIssuesByPriorityWidgetResponse = {
  count: number;
  priority: TIssuePriorities;
};

export type TRecentActivityWidgetResponse = IIssueActivity;

export type TRecentProjectsWidgetResponse = string[];

export type TRecentCollaboratorsWidgetResponse = {
  active_issue_count: number;
  user_id: string;
};

export type TIssuesByStatusWidgetResponse = {
  count: number;
  state_id: string;
  state_name: string;
  state_group: TStateGroups;
  color: string;
};

export type TAssigneeWorkloadWidgetResponse = {
  assignee_id: string;
  assignee_name: string;
  assignee_avatar?: string;
  total_issues: number;
  pending_issues: number;
  in_progress_issues: number;
  completed_issues: number;
};

export type TIssuesTrendWidgetResponse = {
  date: string;
  created: number;
  resolved: number;
};

export type TCycleBurndownWidgetResponse = {
  date: string;
  total: number;
  remaining: number;
  completed: number;
};

export type TVelocityWidgetResponse = {
  date: string;
  completed: number;
  segment: string;
};

export type TLeadTimeWidgetResponse = {
  date: string;
  avg_lead_time: number;
  issues_count: number;
};

export type TCycleTimeWidgetResponse = {
  date: string;
  avg_cycle_time: number;
  issues_count: number;
};

export type TCumulativeFlowWidgetResponse = {
  date: string;
  backlog: number;
  unstarted: number;
  started: number;
  completed: number;
  cancelled: number;
};

export type TWidgetStatsResponse =
  | TOverviewStatsWidgetResponse
  | TIssuesByStateGroupsWidgetResponse[]
  | TIssuesByPriorityWidgetResponse[]
  | TAssignedIssuesWidgetResponse
  | TCreatedIssuesWidgetResponse
  | TRecentActivityWidgetResponse[]
  | TRecentProjectsWidgetResponse
  | TRecentCollaboratorsWidgetResponse[]
  | TIssuesByStatusWidgetResponse[]
  | TAssigneeWorkloadWidgetResponse[]
  | TIssuesTrendWidgetResponse[]
  | TCycleBurndownWidgetResponse[]
  | TVelocityWidgetResponse[]
  | TLeadTimeWidgetResponse[]
  | TCycleTimeWidgetResponse[]
  | TCumulativeFlowWidgetResponse[];

// dashboard
export type TDeprecatedDashboard = {
  created_at: string;
  created_by: string | null;
  description_html: string;
  id: string;
  identifier: string | null;
  is_default: boolean;
  name: string;
  owned_by: string;
  type: string;
  updated_at: string;
  updated_by: string | null;
};

export type THomeDashboardResponse = {
  dashboard: TDeprecatedDashboard;
  widgets: TWidget[];
};

// filter presets
export type TFilterPresetFilters = {
  project?: string[];
  state_group?: string[];
  priority?: string[];
  assignees?: string[];
  created_by?: string[];
  target_date?: string[];
};

export type TFilterPreset = {
  id: string;
  name: string;
  description?: string;
  workspace: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  filters: TFilterPresetFilters;
  is_global: boolean;
};

// dashboard presets
export type TDashboardPresetWidgets = {
  widget_id: string;
  widget_key: TWidgetKeys;
  is_visible: boolean;
  sort_order: number;
  filters: TWidgetFiltersFormData["filters"];
};

export type TDashboardPreset = {
  id: string;
  name: string;
  description?: string;
  workspace: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  is_global: boolean;
  widgets: TDashboardPresetWidgets[];
  active_widget_filter_presets?: string[];
};

// API response types
export type TFilterPresetsResponse = {
  results: TFilterPreset[];
  count: number;
  next: string | null;
  previous: string | null;
};

export type TDashboardPresetsResponse = {
  results: TDashboardPreset[];
  count: number;
  next: string | null;
  previous: string | null;
};

export type TDashboardAccess = 0 | 1 | 2 | 3;

export type TDashboardPermission = "view" | "edit" | "admin";

export type TDashboardSharee = {
  id: string;
  user_id: string;
  permission: TDashboardPermission;
  created_at: string;
  updated_at: string;
};

export type TDashboard = {
  id: string;
  name: string;
  description?: string;
  access: TDashboardAccess;
  owned_by: string;
  created_at: string;
  updated_at: string;
  created_by: string | null;
  updated_by: string | null;
  isarchived: boolean;
  isdeleted: boolean;
  sharees?: TDashboardSharee[];
  embed_code?: string;
};
