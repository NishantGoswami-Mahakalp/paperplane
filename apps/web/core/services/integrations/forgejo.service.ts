/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { IForgejoRepoInfo, IForgejoServiceImportFormData } from "@plane/types";
import { APIService } from "@/services/api.service";

const integrationServiceType: string = "forgejo";

export class ForgejoIntegrationService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async listAllRepositories(workspaceSlug: string, integrationSlug: string): Promise<any> {
    return this.get(`/api/workspaces/${workspaceSlug}/workspace-integrations/${integrationSlug}/forgejo-repositories`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getForgejoRepoInfo(workspaceSlug: string, params: { owner: string; repo: string }): Promise<IForgejoRepoInfo> {
    return this.get(`/api/workspaces/${workspaceSlug}/importers/${integrationServiceType}/`, {
      params,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async createForgejoServiceImport(workspaceSlug: string, data: IForgejoServiceImportFormData): Promise<any> {
    return this.post(`/api/workspaces/${workspaceSlug}/projects/importers/${integrationServiceType}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
