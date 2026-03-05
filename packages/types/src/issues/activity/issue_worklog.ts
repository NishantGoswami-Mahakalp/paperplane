/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type {
  TIssueActivityWorkspaceDetail,
  TIssueActivityProjectDetail,
  TIssueActivityIssueDetail,
  TIssueActivityUserDetail,
} from "./base";

export type TWorklog = {
  id: string;
  workspace: string;
  workspace_detail: TIssueActivityWorkspaceDetail;
  project: string;
  project_detail: TIssueActivityProjectDetail;
  issue: string;
  issue_detail: TIssueActivityIssueDetail;
  actor: string;
  actor_detail: TIssueActivityUserDetail;
  created_at: string;
  updated_at: string;
  created_by: string | undefined;
  updated_by: string | undefined;
  description: string;
  duration: number;
  started_at: string;
  ended_at: string | null;
  is_timer_running: boolean;
};

export type TWorklogMap = {
  [worklog_id: string]: TWorklog;
};

export type TWorklogIdMap = {
  [issue_id: string]: string[];
};

export type TCreateWorklogPayload = {
  description?: string;
  duration?: number;
  started_at?: string;
  ended_at?: string;
};

export type TUpdateWorklogPayload = Partial<TCreateWorklogPayload>;

export type TTimerSession = {
  id: string;
  item_id: string;
  project_id: string;
  workspace_id: string;
  user_id: string;
  started_at: string;
  ended_at: string | null;
  is_running: boolean;
  created_at: string;
  updated_at: string;
};
