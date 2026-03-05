/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

// types
import type { IEpic, IInitiative, TIssuesResponse } from "@plane/types";
// services
import { APIService } from "../api.service";

export class EpicService extends APIService {
  async projectEpicsList(workspaceSlug: string, projectId: string): Promise<IEpic[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(workspaceSlug: string, projectId: string, data: any): Promise<IEpic> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async retrieve(workspaceSlug: string, projectId: string, epicId: string): Promise<IEpic> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(workspaceSlug: string, projectId: string, epicId: string, data: Partial<IEpic>): Promise<IEpic> {
    return this.patch(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async destroy(workspaceSlug: string, projectId: string, epicId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getEpicIssues(
    workspaceSlug: string,
    projectId: string,
    epicId: string,
    queries?: any,
    config = {}
  ): Promise<TIssuesResponse> {
    return this.get(
      `/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/epic-issues/`,
      {
        params: queries,
      },
      config
    )
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async addIssuesToEpic(
    workspaceSlug: string,
    projectId: string,
    epicId: string,
    data: { issues: string[] }
  ): Promise<void> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/epic-issues/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async removeIssuesFromEpic(
    workspaceSlug: string,
    projectId: string,
    epicId: string,
    issueIds: string[]
  ): Promise<void> {
    const promiseDataUrls: any = [];
    issueIds.forEach((issueId) => {
      promiseDataUrls.push(
        this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/epic-issues/${issueId}/`)
      );
    });
    await Promise.all(promiseDataUrls)
      .then((response) => response)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async archive(workspaceSlug: string, projectId: string, epicId: string): Promise<any> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/epics/${epicId}/archive/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async unarchive(workspaceSlug: string, projectId: string, epicId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/archived-epics/${epicId}/unarchive/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async listArchived(workspaceSlug: string, projectId: string): Promise<IEpic[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/archived-epics/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async addEpicToFavorites(
    workspaceSlug: string,
    projectId: string,
    data: {
      epic: string;
    }
  ): Promise<any> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/user-favorite-epics/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async removeEpicFromFavorites(workspaceSlug: string, projectId: string, epicId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/user-favorite-epics/${epicId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}

export class InitiativeService extends APIService {
  async projectInitiativesList(workspaceSlug: string, projectId: string): Promise<IInitiative[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/initiatives/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(workspaceSlug: string, projectId: string, data: any): Promise<IInitiative> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/initiatives/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async retrieve(workspaceSlug: string, projectId: string, initiativeId: string): Promise<IInitiative> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/initiatives/${initiativeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(workspaceSlug: string, projectId: string, initiativeId: string, data: Partial<IInitiative>): Promise<IInitiative> {
    return this.patch(`/api/workspaces/${workspaceSlug}/projects/${projectId}/initiatives/${initiativeId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async destroy(workspaceSlug: string, projectId: string, initiativeId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/initiatives/${initiativeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async addInitiativeToFavorites(
    workspaceSlug: string,
    projectId: string,
    data: {
      initiative: string;
    }
  ): Promise<any> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/user-favorite-initiatives/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async removeInitiativeFromFavorites(workspaceSlug: string, projectId: string, initiativeId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/user-favorite-initiatives/${initiativeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
