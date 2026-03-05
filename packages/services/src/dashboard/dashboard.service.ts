/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type {
  THomeDashboardResponse,
  TWidget,
  TWidgetStatsResponse,
  TWidgetStatsRequestParams,
  TFilterPreset,
  TFilterPresetsResponse,
  TDashboardPreset,
  TDashboardPresetsResponse,
  TDashboard,
  TDashboardAccess,
  TDashboardSharee,
  TDashboardPermission,
} from "@plane/types";
import { APIService } from "../api.service";

export default class DashboardService extends APIService {
  constructor(BASE_URL?: string) {
    super(BASE_URL || API_BASE_URL);
  }

  /**
   * Retrieves home dashboard widgets for a specific workspace
   * @param {string} workspaceSlug - The unique identifier for the workspace
   * @returns {Promise<THomeDashboardResponse>} Promise resolving to dashboard widget data
   * @throws {Error} If the API request fails
   */
  async getHomeWidgets(workspaceSlug: string): Promise<THomeDashboardResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/`, {
      params: {
        dashboard_type: "home",
      },
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  /**
   * Fetches statistics for a specific dashboard widget
   * @param {string} workspaceSlug - The unique identifier for the workspace
   * @param {string} dashboardId - The unique identifier for the dashboard
   * @param {TWidgetStatsRequestParams} params - Parameters for filtering widget statistics
   * @returns {Promise<TWidgetStatsResponse>} Promise resolving to widget statistics data
   * @throws {Error} If the API request fails
   */
  async getWidgetStats(
    workspaceSlug: string,
    dashboardId: string,
    params: TWidgetStatsRequestParams
  ): Promise<TWidgetStatsResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/${dashboardId}/`, {
      params,
    })
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  /**
   * Retrieves detailed information about a specific dashboard
   * @param {string} dashboardId - The unique identifier for the dashboard
   * @returns {Promise<TWidgetStatsResponse>} Promise resolving to dashboard details
   * @throws {Error} If the API request fails
   */
  async retrieve(dashboardId: string): Promise<TWidgetStatsResponse> {
    return this.get(`/api/dashboard/${dashboardId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  /**
   * Updates a specific widget within a dashboard
   * @param {string} dashboardId - The unique identifier for the dashboard
   * @param {string} widgetId - The unique identifier for the widget
   * @param {Partial<TWidget>} data - Partial widget data to update
   * @returns {Promise<TWidget>} Promise resolving to the updated widget data
   * @throws {Error} If the API request fails
   */
  async updateWidget(dashboardId: string, widgetId: string, data: Partial<TWidget>): Promise<TWidget> {
    return this.patch(`/api/dashboard/${dashboardId}/widgets/${widgetId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  // Filter Presets
  async getFilterPresets(workspaceSlug: string): Promise<TFilterPresetsResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/filter-presets/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async createFilterPreset(workspaceSlug: string, data: Partial<TFilterPreset>): Promise<TFilterPreset> {
    return this.post(`/api/workspaces/${workspaceSlug}/dashboard/filter-presets/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getFilterPreset(workspaceSlug: string, presetId: string): Promise<TFilterPreset> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/filter-presets/${presetId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async updateFilterPreset(workspaceSlug: string, presetId: string, data: Partial<TFilterPreset>): Promise<TFilterPreset> {
    return this.patch(`/api/workspaces/${workspaceSlug}/dashboard/filter-presets/${presetId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteFilterPreset(workspaceSlug: string, presetId: string): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/dashboard/filter-presets/${presetId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  // Dashboard Presets
  async getDashboardPresets(workspaceSlug: string): Promise<TDashboardPresetsResponse> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/presets/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async createDashboardPreset(workspaceSlug: string, data: Partial<TDashboardPreset>): Promise<TDashboardPreset> {
    return this.post(`/api/workspaces/${workspaceSlug}/dashboard/presets/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getDashboardPreset(workspaceSlug: string, presetId: string): Promise<TDashboardPreset> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboard/presets/${presetId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async updateDashboardPreset(workspaceSlug: string, presetId: string, data: Partial<TDashboardPreset>): Promise<TDashboardPreset> {
    return this.patch(`/api/workspaces/${workspaceSlug}/dashboard/presets/${presetId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async deleteDashboardPreset(workspaceSlug: string, presetId: string): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/dashboard/presets/${presetId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async updateDashboardAccess(
    workspaceSlug: string,
    dashboardId: string,
    data: { access: TDashboardAccess }
  ): Promise<TDashboard> {
    return this.patch(`/api/workspaces/${workspaceSlug}/dashboards/${dashboardId}/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async shareDashboard(
    workspaceSlug: string,
    dashboardId: string,
    data: { user_ids: string[]; permission: TDashboardPermission }
  ): Promise<TDashboardSharee[]> {
    return this.post(`/api/workspaces/${workspaceSlug}/dashboards/${dashboardId}/share/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async removeShare(
    workspaceSlug: string,
    dashboardId: string,
    shareeId: string
  ): Promise<void> {
    return this.delete(`/api/workspaces/${workspaceSlug}/dashboards/${dashboardId}/share/${shareeId}/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async generateEmbedCode(
    workspaceSlug: string,
    dashboardId: string,
    data: { allow_embed: boolean }
  ): Promise<{ embed_code: string }> {
    return this.post(`/api/workspaces/${workspaceSlug}/dashboards/${dashboardId}/embed/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async getDashboardSharees(workspaceSlug: string, dashboardId: string): Promise<TDashboardSharee[]> {
    return this.get(`/api/workspaces/${workspaceSlug}/dashboards/${dashboardId}/share/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}

export { DashboardService };
