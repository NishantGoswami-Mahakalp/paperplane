/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type {
  TWidgetKeys,
  TWidgetFiltersFormData,
  TWidgetStatsRequestParams,
  TIssuesByStatusWidgetFilters,
  TAssigneeWorkloadWidgetFilters,
  TIssuesTrendWidgetFilters,
  TCycleBurndownWidgetFilters,
  TAssignedIssuesWidgetFilters,
  TCreatedIssuesWidgetFilters,
  TVelocityWidgetFilters,
  TLeadTimeWidgetFilters,
  TCycleTimeWidgetFilters,
  TCumulativeFlowWidgetFilters,
} from "@plane/types";
import { EDurationFilters } from "@plane/constants";

export interface IDashboardQueryBuilder {
  buildQuery(widgetKey: TWidgetKeys, filters: Partial<TWidgetFiltersFormData>): TWidgetStatsRequestParams;
  getDateRange(filters: { duration?: EDurationFilters; custom_dates?: string[] }): string;
}

export class DashboardQueryBuilder implements IDashboardQueryBuilder {
  private getDateParam(filters: { duration?: EDurationFilters; custom_dates?: string[] }): string {
    if (filters.duration === EDurationFilters.CUSTOM && filters.custom_dates && filters.custom_dates.length > 0) {
      return filters.custom_dates[0];
    }
    if (filters.duration && filters.duration !== EDurationFilters.NONE) {
      const today = new Date();
      switch (filters.duration) {
        case EDurationFilters.TODAY:
          return today.toISOString().split("T")[0];
        case EDurationFilters.THIS_WEEK: {
          const startOfWeek = new Date(today);
          startOfWeek.setDate(today.getDate() - today.getDay());
          return startOfWeek.toISOString().split("T")[0];
        }
        case EDurationFilters.THIS_MONTH: {
          const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1);
          return startOfMonth.toISOString().split("T")[0];
        }
        case EDurationFilters.THIS_YEAR: {
          const startOfYear = new Date(today.getFullYear(), 0, 1);
          return startOfYear.toISOString().split("T")[0];
        }
        default:
          return today.toISOString().split("T")[0];
      }
    }
    return new Date().toISOString().split("T")[0];
  }

  getDateRange(filters: { duration?: EDurationFilters; custom_dates?: string[] }): string {
    return this.getDateParam(filters);
  }

  buildQuery(widgetKey: TWidgetKeys, filters: Partial<TWidgetFiltersFormData>): TWidgetStatsRequestParams {
    const targetDate = this.getDateParam(filters as { duration?: EDurationFilters; custom_dates?: string[] });

    switch (widgetKey) {
      case "issues_by_status": {
        const statusFilters = filters as Partial<TIssuesByStatusWidgetFilters>;
        return {
          widget_key: "issues_by_status",
          target_date: targetDate,
          project_ids: statusFilters?.project_ids,
        };
      }
      case "assignee_workload": {
        const assigneeFilters = filters as Partial<TAssigneeWorkloadWidgetFilters>;
        return {
          widget_key: "assignee_workload",
          target_date: targetDate,
          project_ids: assigneeFilters?.project_ids,
          assignees: assigneeFilters?.assignees,
        };
      }
      case "issues_trend": {
        const trendFilters = filters as Partial<TIssuesTrendWidgetFilters>;
        return {
          widget_key: "issues_trend",
          target_date: targetDate,
          project_ids: trendFilters?.project_ids,
          segment_by: trendFilters?.segment_by,
        };
      }
      case "cycle_burndown": {
        const burndownFilters = filters as Partial<TCycleBurndownWidgetFilters>;
        return {
          widget_key: "cycle_burndown",
          target_date: targetDate,
          cycle_id: burndownFilters?.cycle_id || "",
          project_ids: burndownFilters?.project_ids,
          plot_type: burndownFilters?.plot_type || "burndown",
        };
      }
      case "issues_by_state_groups": {
        return {
          widget_key: "issues_by_state_groups",
          target_date: targetDate,
        };
      }
      case "issues_by_priority": {
        return {
          widget_key: "issues_by_priority",
          target_date: targetDate,
        };
      }
      case "assigned_issues": {
        const assignedFilters = filters as Partial<TAssignedIssuesWidgetFilters>;
        return {
          widget_key: "assigned_issues",
          target_date: targetDate,
          issue_type: assignedFilters?.tab || "pending",
        };
      }
      case "created_issues": {
        const createdFilters = filters as Partial<TCreatedIssuesWidgetFilters>;
        return {
          widget_key: "created_issues",
          target_date: targetDate,
          issue_type: createdFilters?.tab || "pending",
        };
      }
      case "velocity": {
        const velocityFilters = filters as Partial<TVelocityWidgetFilters>;
        return {
          widget_key: "velocity",
          target_date: targetDate,
          project_ids: velocityFilters?.project_ids,
          segment_by: velocityFilters?.segment_by || "week",
        };
      }
      case "lead_time": {
        const leadTimeFilters = filters as Partial<TLeadTimeWidgetFilters>;
        return {
          widget_key: "lead_time",
          target_date: targetDate,
          project_ids: leadTimeFilters?.project_ids,
        };
      }
      case "cycle_time": {
        const cycleTimeFilters = filters as Partial<TCycleTimeWidgetFilters>;
        return {
          widget_key: "cycle_time",
          target_date: targetDate,
          project_ids: cycleTimeFilters?.project_ids,
        };
      }
      case "cumulative_flow": {
        const cumulativeFlowFilters = filters as Partial<TCumulativeFlowWidgetFilters>;
        return {
          widget_key: "cumulative_flow",
          target_date: targetDate,
          project_ids: cumulativeFlowFilters?.project_ids,
        };
      }
      default:
        return { widget_key: widgetKey };
    }
  }
}

export const dashboardQueryBuilder = new DashboardQueryBuilder();
