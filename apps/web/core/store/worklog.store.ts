/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { action, observable, makeObservable, runInAction } from "mobx";
import type { TWorklog, TCreateWorklogPayload, TUpdateWorklogPayload } from "@plane/types";
import { worklogService, type TTimerSession } from "@/services/worklog.service";

export interface IWorklogStore {
  worklogs: Record<string, TWorklog[]>;
  runningTimers: Record<string, TTimerSession>;
  isLoading: boolean;
  isTimerLoading: boolean;

  getWorklogs: (workspaceSlug: string, projectId: string, issueId: string) => TWorklog[];
  getRunningTimer: (workspaceSlug: string, projectId: string, issueId: string) => TTimerSession | null;
  fetchWorklogs: (workspaceSlug: string, projectId: string, issueId: string) => Promise<void>;
  fetchRunningTimer: (workspaceSlug: string, projectId: string, issueId: string) => Promise<void>;
  startTimer: (workspaceSlug: string, projectId: string, issueId: string) => Promise<void>;
  stopTimer: (workspaceSlug: string, projectId: string, issueId: string, description?: string) => Promise<TWorklog | null>;
  createWorklog: (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    data: TCreateWorklogPayload
  ) => Promise<TWorklog>;
  updateWorklog: (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    worklogId: string,
    data: TUpdateWorklogPayload
  ) => Promise<TWorklog>;
  deleteWorklog: (workspaceSlug: string, projectId: string, issueId: string, worklogId: string) => Promise<void>;
  clearWorklogs: (issueId: string) => void;
}

const getIssueKey = (workspaceSlug: string, projectId: string, issueId: string) =>
  `${workspaceSlug}-${projectId}-${issueId}`;

export class WorklogStore implements IWorklogStore {
  worklogs: Record<string, TWorklog[]> = {};
  runningTimers: Record<string, TTimerSession> = {};
  isLoading: boolean = false;
  isTimerLoading: boolean = false;

  constructor() {
    makeObservable(this, {
      worklogs: observable,
      runningTimers: observable,
      isLoading: observable,
      isTimerLoading: observable,
      fetchWorklogs: action,
      fetchRunningTimer: action,
      startTimer: action,
      stopTimer: action,
      createWorklog: action,
      updateWorklog: action,
      deleteWorklog: action,
      clearWorklogs: action,
    });
  }

  getWorklogs = (workspaceSlug: string, projectId: string, issueId: string): TWorklog[] => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    return this.worklogs[key] || [];
  };

  getRunningTimer = (workspaceSlug: string, projectId: string, issueId: string): TTimerSession | null => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    return this.runningTimers[key] || null;
  };

  fetchWorklogs = async (workspaceSlug: string, projectId: string, issueId: string) => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isLoading = true;
      });
      const response = await worklogService.listWorklogs(workspaceSlug, projectId, issueId);
      runInAction(() => {
        this.worklogs[key] = response;
        this.isLoading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.isLoading = false;
      });
      console.error("Failed to fetch worklogs:", error);
      throw error;
    }
  };

  fetchRunningTimer = async (workspaceSlug: string, projectId: string, issueId: string) => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isTimerLoading = true;
      });
      const response = await worklogService.getRunningTimer(workspaceSlug, projectId, issueId);
      runInAction(() => {
        if (response) {
          this.runningTimers[key] = response;
        } else {
          delete this.runningTimers[key];
        }
        this.isTimerLoading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.isTimerLoading = false;
      });
      console.error("Failed to fetch running timer:", error);
      throw error;
    }
  };

  startTimer = async (workspaceSlug: string, projectId: string, issueId: string) => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isTimerLoading = true;
      });
      const response = await worklogService.startTimer(workspaceSlug, projectId, issueId);
      runInAction(() => {
        this.runningTimers[key] = response;
        this.isTimerLoading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.isTimerLoading = false;
      });
      console.error("Failed to start timer:", error);
      throw error;
    }
  };

  stopTimer = async (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    description?: string
  ): Promise<TWorklog | null> => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isTimerLoading = true;
      });
      const response = await worklogService.stopTimer(workspaceSlug, projectId, issueId, { description });
      runInAction(() => {
        delete this.runningTimers[key];
        if (response.worklog) {
          const existingWorklogs = this.worklogs[key] || [];
          this.worklogs[key] = [response.worklog, ...existingWorklogs];
        }
        this.isTimerLoading = false;
      });
      return response.worklog;
    } catch (error) {
      runInAction(() => {
        this.isTimerLoading = false;
      });
      console.error("Failed to stop timer:", error);
      throw error;
    }
  };

  createWorklog = async (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    data: TCreateWorklogPayload
  ): Promise<TWorklog> => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isLoading = true;
      });
      const response = await worklogService.createWorklog(workspaceSlug, projectId, issueId, data);
      runInAction(() => {
        const existingWorklogs = this.worklogs[key] || [];
        this.worklogs[key] = [response, ...existingWorklogs];
        this.isLoading = false;
      });
      return response;
    } catch (error) {
      runInAction(() => {
        this.isLoading = false;
      });
      console.error("Failed to create worklog:", error);
      throw error;
    }
  };

  updateWorklog = async (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    worklogId: string,
    data: TUpdateWorklogPayload
  ): Promise<TWorklog> => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isLoading = true;
      });
      const response = await worklogService.updateWorklog(workspaceSlug, projectId, issueId, worklogId, data);
      runInAction(() => {
        const worklogs = this.worklogs[key] || [];
        const index = worklogs.findIndex((w) => w.id === worklogId);
        if (index !== -1) {
          worklogs[index] = response;
          this.worklogs[key] = [...worklogs];
        }
        this.isLoading = false;
      });
      return response;
    } catch (error) {
      runInAction(() => {
        this.isLoading = false;
      });
      console.error("Failed to update worklog:", error);
      throw error;
    }
  };

  deleteWorklog = async (
    workspaceSlug: string,
    projectId: string,
    issueId: string,
    worklogId: string
  ): Promise<void> => {
    const key = getIssueKey(workspaceSlug, projectId, issueId);
    try {
      runInAction(() => {
        this.isLoading = true;
      });
      await worklogService.deleteWorklog(workspaceSlug, projectId, issueId, worklogId);
      runInAction(() => {
        const worklogs = this.worklogs[key] || [];
        this.worklogs[key] = worklogs.filter((w) => w.id !== worklogId);
        this.isLoading = false;
      });
    } catch (error) {
      runInAction(() => {
        this.isLoading = false;
      });
      console.error("Failed to delete worklog:", error);
      throw error;
    }
  };

  clearWorklogs = (issueId: string) => {
    Object.keys(this.worklogs).forEach((key) => {
      if (key.endsWith(issueId)) {
        delete this.worklogs[key];
      }
    });
    Object.keys(this.runningTimers).forEach((key) => {
      if (key.endsWith(issueId)) {
        delete this.runningTimers[key];
      }
    });
  };
}

export const worklogStore = new WorklogStore();
