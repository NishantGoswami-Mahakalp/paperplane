/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { IIntakeForm } from "@plane/types";
import { APIService } from "@/services/api.service";

export class IntakeFormService extends APIService {
  constructor(BASE_URL?: string) {
    super(BASE_URL || API_BASE_URL);
  }

  async list(workspaceSlug: string, projectId: string): Promise<IIntakeForm> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/intakes/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async create(workspaceSlug: string, projectId: string, data: Partial<IIntakeForm>): Promise<IIntakeForm> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/${projectId}/intakes/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async retrieve(workspaceSlug: string, projectId: string, intakeId: string): Promise<IIntakeForm> {
    return this.get(`/api/workspaces/${workspaceSlug}/projects/${projectId}/intakes/${intakeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async update(
    workspaceSlug: string,
    projectId: string,
    intakeId: string,
    data: Partial<IIntakeForm>
  ): Promise<IIntakeForm> {
    return this.patch(`/api/workspaces/${workspaceSlug}/projects/${projectId}/intakes/${intakeId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async destroy(workspaceSlug: string, projectId: string, intakeId: string): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/projects/${projectId}/intakes/${intakeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
