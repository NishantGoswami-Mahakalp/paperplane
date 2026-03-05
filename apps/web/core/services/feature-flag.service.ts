/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { EFeatureFlag, IFeatureFlagInput, IFeatureFlagsResponse, TFeatureFlagLevel } from "@plane/types";
import { APIService } from "@/services/api.service";

export class FeatureService extends APIService {
  constructor() {
    super(API_BASE_URL);
  }

  async getFeatureFlags(workspaceSlug: string): Promise<IFeatureFlagsResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/feature-flags/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async setFeatureFlag(
    workspaceSlug: string,
    data: IFeatureFlagInput
  ): Promise<{ success: boolean }> {
    return this.post(`/api/workspaces/${workspaceSlug}/feature-flags/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async updateFeatureFlag(
    workspaceSlug: string,
    featureFlag: EFeatureFlag,
    data: { enabled: boolean; level: TFeatureFlagLevel; entity_id: string }
  ): Promise<{ success: boolean }> {
    return this.patch(`/api/workspaces/${workspaceSlug}/feature-flags/${featureFlag}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteFeatureFlag(
    workspaceSlug: string,
    featureFlag: EFeatureFlag,
    entityId: string,
    level: TFeatureFlagLevel
  ): Promise<{ success: boolean }> {
    return this.delete(`/api/workspaces/${workspaceSlug}/feature-flags/${featureFlag}/`, {
      entity_id: entityId,
      level,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getUserFeatureFlags(userId: string): Promise<Record<EFeatureFlag, boolean>> {
    return this.get(`/api/users/${userId}/feature-flags/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async setUserFeatureFlag(
    userId: string,
    featureFlag: EFeatureFlag,
    enabled: boolean
  ): Promise<{ success: boolean }> {
    return this.post(`/api/users/${userId}/feature-flags/`, {
      feature_flag: featureFlag,
      enabled,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}

export const featureService = new FeatureService();
