/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { IIssueFilterOptions } from "./view-props";

export type TEpicStatus = "backlog" | "planned" | "in-progress" | "completed" | "cancelled";

export type TEpicAnalyticsGroup =
  | "backlog_issues"
  | "unstarted_issues"
  | "started_issues"
  | "completed_issues"
  | "cancelled_issues"
  | "overdue_issues";

export type TEpicAnalytics = {
  backlog_issues: number;
  unstarted_issues: number;
  started_issues: number;
  completed_issues: number;
  cancelled_issues: number;
  overdue_issues: number;
};

export type TEpicProgress = {
  total_issues: number;
  completed_issues: number;
  backlog_issues: number;
  started_issues: number;
  unstarted_issues: number;
  cancelled_issues: number;
};

export interface IEpic extends TEpicProgress {
  id: string;
  name: string;
  description: string;
  description_html: string | null;
  description_json: object | null;
  workspace_id: string;
  project_id: string;
  initiative_id: string | null;
  start_date: string | null;
  target_date: string | null;
  status: TEpicStatus;
  lead_id: string | null;
  member_ids: string[];
  is_favorite: boolean;
  sort_order: number;
  view_props: {
    filters: IIssueFilterOptions;
  };
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

export interface EpicIssueResponse {
  id: string;
  epic: string;
  epic_detail: IEpic;
  issue: string;
  issue_detail: any;
  project: string;
  workspace: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

export type TInitiativeStatus = "backlog" | "planned" | "in-progress" | "completed" | "cancelled";

export type TInitiativeProgress = {
  total_epics: number;
  completed_epics: number;
  backlog_epics: number;
  started_epics: number;
  cancelled_epics: number;
  total_issues: number;
  completed_issues: number;
};

export interface IInitiative extends TInitiativeProgress {
  id: string;
  name: string;
  description: string;
  description_html: string | null;
  description_json: object | null;
  workspace_id: string;
  project_id: string;
  start_date: string | null;
  target_date: string | null;
  status: TInitiativeStatus;
  lead_id: string | null;
  member_ids: string[];
  is_favorite: boolean;
  sort_order: number;
  view_props: {
    filters: IIssueFilterOptions;
  };
  archived_at: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

export interface InitiativeEpicResponse {
  id: string;
  initiative: string;
  initiative_detail: IInitiative;
  epic: string;
  epic_detail: IEpic;
  project: string;
  workspace: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  updated_by: string;
}

export type SelectEpicType = (IEpic & { actionType: "edit" | "delete" | "create-issue" }) | undefined;

export type SelectInitiativeType = (IInitiative & { actionType: "edit" | "delete" | "create-epic" }) | undefined;
