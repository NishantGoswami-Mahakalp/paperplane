/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { TCreateWorklogPayload, TWorklog, TUpdateWorklogPayload } from "@plane/types";
import { APIService } from "../api.service";

export interface TTimerSession {
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
}

export interface TTimerStartResponse {
  id: string;
  item_id: string;
  project_id: string;
  workspace_id: string;
  user_id: string;
  started_at: string;
  ended_at: string | null;
  is_running: boolean;
}

export interface TTimerStopResponse {
  timer: TTimerSession;
  worklog: TWorklog;
}

export interface TWorklogFilters {
  cursor?: string;
  per_page?: number;
  started_after?: string;
  started_before?: string;
}

export class WorklogService extends APIService {
  constructor(BASE_URL?: string) {
    super(BASE_URL || API_BASE_URL);
  }

  async startTimer(
    workspaceSlug: string,
    projectId: string,
    itemId: string,
    data?: { started_at?: string }
  ): Promise<TTimerStartResponse> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/timer/start/`, data ?? {})
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async stopTimer(
    workspaceSlug: string,
    projectId: string,
    itemId: string,
    data?: { ended_at?: string; description?: string }
  ): Promise<TTimerStopResponse> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/timer/stop/`, data ?? {})
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getRunningTimer(workspaceSlug: string, projectId: string, itemId: string): Promise<TTimerSession | null> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/timer/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async listWorklogs(
    workspaceSlug: string,
    projectId: string,
    itemId: string,
    params?: TWorklogFilters
  ): Promise<TWorklog[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/worklogs/`, {
      params,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async createWorklog(
    workspaceSlug: string,
    projectId: string,
    itemId: string,
    data: TCreateWorklogPayload
  ): Promise<TWorklog> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/worklogs/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async updateWorklog(
    workspaceSlug: string,
    projectId: string,
    itemId: string,
    worklogId: string,
    data: TUpdateWorklogPayload
  ): Promise<TWorklog> {
    return this.patch(
      `/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/worklogs/${worklogId}/`,
      data
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteWorklog(workspaceSlug: string, projectId: string, itemId: string, worklogId: string): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/worklogs/${worklogId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getWorklog(workspaceSlug: string, projectId: string, itemId: string, worklogId: string): Promise<TWorklog> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/items/${itemId}/worklogs/${worklogId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
