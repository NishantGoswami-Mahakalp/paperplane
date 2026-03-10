/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { IAppIntegration, IImporterService, IExportServiceResponse } from "@plane/types";
import { APIService } from "@/services/api.service";

const APP_INTEGRATIONS: IAppIntegration[] = [
  {
    id: "github",
    provider: "github",
    title: "GitHub",
    description: "Connect GitHub repositories and sync project work items.",
    author: "PaperPlane",
    avatar_url: null,
    created_at: "",
    created_by: null,
    metadata: null,
    network: 0,
    redirect_url: "",
    updated_at: "",
    updated_by: null,
    verified: true,
    webhook_secret: "",
    webhook_url: "",
  },
  {
    id: "slack",
    provider: "slack",
    title: "Slack",
    description: "Connect Slack channels and sync project activity.",
    author: "PaperPlane",
    avatar_url: null,
    created_at: "",
    created_by: null,
    metadata: null,
    network: 0,
    redirect_url: "",
    updated_at: "",
    updated_by: null,
    verified: true,
    webhook_secret: "",
    webhook_url: "",
  },
  {
    id: "forgejo",
    provider: "forgejo",
    title: "Forgejo",
    description: "Connect Forgejo repositories and import project work items.",
    author: "PaperPlane",
    avatar_url: null,
    created_at: "",
    created_by: null,
    metadata: null,
    network: 0,
    redirect_url: "",
    updated_at: "",
    updated_by: null,
    verified: true,
    webhook_secret: "",
    webhook_url: "",
  },
];

export class IntegrationService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async getAppIntegrationsList(): Promise<IAppIntegration[]> {
    return Promise.resolve(APP_INTEGRATIONS);
  }

  async getImporterServicesList(workspaceSlug: string): Promise<IImporterService[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/importers/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
  async getExportsServicesList(
    workspaceSlug: string,
    cursor: string,
    per_page: number
  ): Promise<IExportServiceResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/export-issues`, {
      params: {
        per_page,
        cursor,
      },
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteImporterService(workspaceSlug: string, service: string, importerId: string): Promise<any> {
    return this.delete(`/api/workspaces/${workspaceSlug}/importers/${service}/${importerId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
