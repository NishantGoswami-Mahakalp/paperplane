/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { set } from "lodash-es";
import { action, computed, makeObservable, observable, runInAction } from "mobx";
import { computedFn } from "mobx-utils";
// types
import type {
  THomeDashboardResponse,
  TWidget,
  TWidgetFiltersFormData,
  TWidgetStatsResponse,
  TWidgetKeys,
  TWidgetStatsRequestParams,
  TFilterPreset,
  TDashboardPreset,
  TDashboardAccess,
  TDashboardSharee,
  TDashboardPermission,
} from "@plane/types";
// services
import { DashboardService } from "@/services/dashboard.service";
// plane web store
import type { CoreRootStore } from "./root.store";

export interface IDashboardStore {
  // error states
  widgetStatsError: { [workspaceSlug: string]: Record<string, Record<TWidgetKeys, any | null>> };
  // observables
  homeDashboardId: string | null;
  widgetDetails: { [workspaceSlug: string]: Record<string, TWidget[]> };
  // {
  //  workspaceSlug: {
  //    dashboardId: TWidget[]
  //   }
  // }
  widgetStats: { [workspaceSlug: string]: Record<string, Record<TWidgetKeys, TWidgetStatsResponse>> };
  //  {
  //    workspaceSlug: {
  //      dashboardId: {
  //        widgetKey: TWidgetStatsResponse;
  //        }
  //     }
  //  }
  // filter presets
  filterPresets: { [workspaceSlug: string]: TFilterPreset[] };
  // dashboard presets
  dashboardPresets: { [workspaceSlug: string]: TDashboardPreset[] };
  // current active preset
  activeFilterPresetId: string | null;
  activeDashboardPresetId: string | null;
  // computed
  homeDashboardWidgets: TWidget[] | undefined;
  // computed actions
  getWidgetDetails: (workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys) => TWidget | undefined;
  getWidgetStats: <T>(workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys) => T | undefined;
  getWidgetStatsError: (workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys) => any | null;
  // actions
  fetchHomeDashboardWidgets: (workspaceSlug: string) => Promise<THomeDashboardResponse>;
  fetchWidgetStats: (
    workspaceSlug: string,
    dashboardId: string,
    params: TWidgetStatsRequestParams
  ) => Promise<TWidgetStatsResponse>;
  updateDashboardWidget: (
    workspaceSlug: string,
    dashboardId: string,
    widgetId: string,
    data: Partial<TWidget>
  ) => Promise<any>;
  updateDashboardWidgetFilters: (
    workspaceSlug: string,
    dashboardId: string,
    widgetId: string,
    data: TWidgetFiltersFormData
  ) => Promise<any>;
  // filter preset actions
  fetchFilterPresets: (workspaceSlug: string) => Promise<TFilterPreset[]>;
  createFilterPreset: (workspaceSlug: string, data: Partial<TFilterPreset>) => Promise<TFilterPreset>;
  updateFilterPreset: (workspaceSlug: string, presetId: string, data: Partial<TFilterPreset>) => Promise<TFilterPreset>;
  deleteFilterPreset: (workspaceSlug: string, presetId: string) => Promise<void>;
  setActiveFilterPreset: (presetId: string | null) => void;
  // dashboard preset actions
  fetchDashboardPresets: (workspaceSlug: string) => Promise<TDashboardPreset[]>;
  createDashboardPreset: (workspaceSlug: string, data: Partial<TDashboardPreset>) => Promise<TDashboardPreset>;
  updateDashboardPreset: (workspaceSlug: string, presetId: string, data: Partial<TDashboardPreset>) => Promise<TDashboardPreset>;
  deleteDashboardPreset: (workspaceSlug: string, presetId: string) => Promise<void>;
  setActiveDashboardPreset: (presetId: string | null) => void;
  applyDashboardPreset: (workspaceSlug: string, preset: TDashboardPreset) => Promise<void>;
  updateDashboardAccess: (workspaceSlug: string, dashboardId: string, access: TDashboardAccess) => Promise<void>;
  shareDashboard: (workspaceSlug: string, dashboardId: string, userIds: string[], permission: TDashboardPermission) => Promise<TDashboardSharee[]>;
  removeShare: (workspaceSlug: string, dashboardId: string, shareeId: string) => Promise<void>;
  generateEmbedCode: (workspaceSlug: string, dashboardId: string, allowEmbed: boolean) => Promise<string>;
  getDashboardSharees: (workspaceSlug: string, dashboardId: string) => Promise<TDashboardSharee[]>;
}

export class DashboardStore implements IDashboardStore {
  // error states
  widgetStatsError: { [workspaceSlug: string]: Record<string, Record<TWidgetKeys, any>> } = {};
  // observables
  homeDashboardId: string | null = null;
  widgetDetails: { [workspaceSlug: string]: Record<string, TWidget[]> } = {};
  widgetStats: { [workspaceSlug: string]: Record<string, Record<TWidgetKeys, TWidgetStatsResponse>> } = {};
  // filter presets
  filterPresets: { [workspaceSlug: string]: TFilterPreset[] } = {};
  // dashboard presets
  dashboardPresets: { [workspaceSlug: string]: TDashboardPreset[] } = {};
  // current active preset
  activeFilterPresetId: string | null = null;
  activeDashboardPresetId: string | null = null;
  // stores
  routerStore;
  issueStore;
  // services
  dashboardService;

  constructor(_rootStore: CoreRootStore) {
    makeObservable(this, {
      // error states
      widgetStatsError: observable,
      // observables
      homeDashboardId: observable.ref,
      widgetDetails: observable,
      widgetStats: observable,
      // filter presets
      filterPresets: observable,
      // dashboard presets
      dashboardPresets: observable,
      // active presets
      activeFilterPresetId: observable.ref,
      activeDashboardPresetId: observable.ref,
      // computed
      homeDashboardWidgets: computed,
      // fetch actions
      fetchHomeDashboardWidgets: action,
      fetchWidgetStats: action,
      // update actions
      updateDashboardWidget: action,
      updateDashboardWidgetFilters: action,
      // filter preset actions
      fetchFilterPresets: action,
      createFilterPreset: action,
      updateFilterPreset: action,
      deleteFilterPreset: action,
      setActiveFilterPreset: action,
      // dashboard preset actions
      fetchDashboardPresets: action,
      createDashboardPreset: action,
      updateDashboardPreset: action,
      deleteDashboardPreset: action,
      setActiveDashboardPreset: action,
      applyDashboardPreset: action,
    });

    // router store
    this.routerStore = _rootStore.router;
    this.issueStore = _rootStore.issue.issues;
    // services
    this.dashboardService = new DashboardService();
  }

  /**
   * @description get home dashboard widgets
   * @returns {TWidget[] | undefined}
   */
  get homeDashboardWidgets() {
    const workspaceSlug = this.routerStore.workspaceSlug;
    if (!workspaceSlug) return undefined;
    const { homeDashboardId, widgetDetails } = this;
    return homeDashboardId ? widgetDetails?.[workspaceSlug]?.[homeDashboardId] : undefined;
  }

  /**
   * @description get widget details
   * @param {string} workspaceSlug
   * @param {string} dashboardId
   * @param {TWidgetKeys} widgetKey
   * @returns {TWidget | undefined}
   */
  getWidgetDetails = computedFn((workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys) => {
    const widgets = this.widgetDetails?.[workspaceSlug]?.[dashboardId];
    if (!widgets) return undefined;
    return widgets.find((widget) => widget.key === widgetKey);
  });

  /**
   * @description get widget stats
   * @param {string} workspaceSlug
   * @param {string} dashboardId
   * @param {TWidgetKeys} widgetKey
   * @returns {T | undefined}
   */
  getWidgetStats = <T>(workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys): T | undefined =>
    (this.widgetStats?.[workspaceSlug]?.[dashboardId]?.[widgetKey] as unknown as T) ?? undefined;

  /**
   * @description get widget stats error
   * @param {string} workspaceSlug
   * @param {string} dashboardId
   * @param {TWidgetKeys} widgetKey
   * @returns {any | null}
   */
  getWidgetStatsError = (workspaceSlug: string, dashboardId: string, widgetKey: TWidgetKeys) =>
    this.widgetStatsError?.[workspaceSlug]?.[dashboardId]?.[widgetKey] ?? null;

  /**
   * @description fetch home dashboard details and widgets
   * @param {string} workspaceSlug
   * @returns {Promise<THomeDashboardResponse>}
   */
  fetchHomeDashboardWidgets = async (workspaceSlug: string): Promise<THomeDashboardResponse> => {
    try {
      const response = await this.dashboardService.getHomeDashboardWidgets(workspaceSlug);

      runInAction(() => {
        this.homeDashboardId = response.dashboard.id;
        set(this.widgetDetails, [workspaceSlug, response.dashboard.id], response.widgets);
      });

      return response;
    } catch (error) {
      runInAction(() => {
        this.homeDashboardId = null;
      });

      throw error;
    }
  };

  /**
   * @description fetch widget stats
   * @param {string} workspaceSlug
   * @param {string} dashboardId
   * @param {TWidgetStatsRequestParams} widgetKey
   * @returns widget stats
   */
  fetchWidgetStats = async (workspaceSlug: string, dashboardId: string, params: TWidgetStatsRequestParams) =>
    this.dashboardService
      .getWidgetStats(workspaceSlug, dashboardId, params)
      .then((res: any) => {
        runInAction(() => {
          if (res.issues) this.issueStore.addIssue(res.issues);
          set(this.widgetStats, [workspaceSlug, dashboardId, params.widget_key], res);
          set(this.widgetStatsError, [workspaceSlug, dashboardId, params.widget_key], null);
        });
        return res;
      })
      .catch((error) => {
        runInAction(() => {
          set(this.widgetStatsError, [workspaceSlug, dashboardId, params.widget_key], error);
        });

        throw error;
      });

  /**
   * @description update dashboard widget
   * @param {string} dashboardId
   * @param {string} widgetId
   * @param {Partial<TWidget>} data
   * @returns updated widget
   */
  updateDashboardWidget = async (
    workspaceSlug: string,
    dashboardId: string,
    widgetId: string,
    data: Partial<TWidget>
  ): Promise<any> => {
    // find all widgets in dashboard
    const widgets = this.widgetDetails?.[workspaceSlug]?.[dashboardId];
    if (!widgets) throw new Error("Dashboard not found");
    // find widget index
    const widgetIndex = widgets.findIndex((widget) => widget.id === widgetId);
    // get original widget
    const originalWidget = { ...widgets[widgetIndex] };
    if (widgetIndex === -1) throw new Error("Widget not found");

    try {
      runInAction(() => {
        this.widgetDetails[workspaceSlug][dashboardId][widgetIndex] = {
          ...widgets[widgetIndex],
          ...data,
        };
      });
      const response = await this.dashboardService.updateDashboardWidget(dashboardId, widgetId, data);
      return response;
    } catch (error) {
      // revert changes
      runInAction(() => {
        this.widgetDetails[workspaceSlug][dashboardId][widgetIndex] = originalWidget;
      });
      throw error;
    }
  };

  /**
   * @description update dashboard widget filters
   * @param {string} dashboardId
   * @param {string} widgetId
   * @param {TWidgetFiltersFormData} data
   * @returns updated widget
   */
  updateDashboardWidgetFilters = async (
    workspaceSlug: string,
    dashboardId: string,
    widgetId: string,
    data: TWidgetFiltersFormData
  ): Promise<TWidget> => {
    const widgetDetails = this.getWidgetDetails(workspaceSlug, dashboardId, data.widgetKey);
    if (!widgetDetails) throw new Error("Widget not found");
    try {
      const updatedWidget = {
        ...widgetDetails,
        widget_filters: {
          ...widgetDetails.widget_filters,
          ...data.filters,
        },
      };
      // update widget details optimistically
      runInAction(() => {
        set(
          this.widgetDetails,
          [workspaceSlug, dashboardId],
          this.widgetDetails?.[workspaceSlug]?.[dashboardId]?.map((w) => (w.id === widgetId ? updatedWidget : w))
        );
      });
      const response = await this.updateDashboardWidget(workspaceSlug, dashboardId, widgetId, {
        filters: {
          ...widgetDetails.widget_filters,
          ...data.filters,
        },
      }).then((res) => res);

      return response;
    } catch (error) {
      // revert changes
      runInAction(() => {
        this.widgetDetails[workspaceSlug][dashboardId] = this.widgetDetails?.[workspaceSlug]?.[dashboardId]?.map((w) =>
          w.id === widgetId ? widgetDetails : w
        );
      });
      throw error;
    }
  };

  // Filter Preset Actions
  fetchFilterPresets = async (workspaceSlug: string): Promise<TFilterPreset[]> => {
    try {
      const response = await this.dashboardService.getFilterPresets(workspaceSlug);
      runInAction(() => {
        this.filterPresets[workspaceSlug] = response.results;
      });
      return response.results;
    } catch (error) {
      console.error("Failed to fetch filter presets", error);
      throw error;
    }
  };

  createFilterPreset = async (workspaceSlug: string, data: Partial<TFilterPreset>): Promise<TFilterPreset> => {
    try {
      const response = await this.dashboardService.createFilterPreset(workspaceSlug, data);
      runInAction(() => {
        if (!this.filterPresets[workspaceSlug]) {
          this.filterPresets[workspaceSlug] = [];
        }
        this.filterPresets[workspaceSlug].push(response);
      });
      return response;
    } catch (error) {
      console.error("Failed to create filter preset", error);
      throw error;
    }
  };

  updateFilterPreset = async (
    workspaceSlug: string,
    presetId: string,
    data: Partial<TFilterPreset>
  ): Promise<TFilterPreset> => {
    const originalPresets = { ...this.filterPresets };
    try {
      const response = await this.dashboardService.updateFilterPreset(workspaceSlug, presetId, data);
      runInAction(() => {
        const index = this.filterPresets[workspaceSlug]?.findIndex((p) => p.id === presetId);
        if (index !== undefined && index !== -1) {
          this.filterPresets[workspaceSlug][index] = response;
        }
      });
      return response;
    } catch (error) {
      runInAction(() => {
        this.filterPresets = originalPresets;
      });
      console.error("Failed to update filter preset", error);
      throw error;
    }
  };

  deleteFilterPreset = async (workspaceSlug: string, presetId: string): Promise<void> => {
    const originalPresets = [...(this.filterPresets[workspaceSlug] || [])];
    try {
      await this.dashboardService.deleteFilterPreset(workspaceSlug, presetId);
      runInAction(() => {
        this.filterPresets[workspaceSlug] = this.filterPresets[workspaceSlug]?.filter((p) => p.id !== presetId);
        if (this.activeFilterPresetId === presetId) {
          this.activeFilterPresetId = null;
        }
      });
    } catch (error) {
      runInAction(() => {
        this.filterPresets[workspaceSlug] = originalPresets;
      });
      console.error("Failed to delete filter preset", error);
      throw error;
    }
  };

  setActiveFilterPreset = (presetId: string | null) => {
    this.activeFilterPresetId = presetId;
  };

  // Dashboard Preset Actions
  fetchDashboardPresets = async (workspaceSlug: string): Promise<TDashboardPreset[]> => {
    try {
      const response = await this.dashboardService.getDashboardPresets(workspaceSlug);
      runInAction(() => {
        this.dashboardPresets[workspaceSlug] = response.results;
      });
      return response.results;
    } catch (error) {
      console.error("Failed to fetch dashboard presets", error);
      throw error;
    }
  };

  createDashboardPreset = async (workspaceSlug: string, data: Partial<TDashboardPreset>): Promise<TDashboardPreset> => {
    try {
      const response = await this.dashboardService.createDashboardPreset(workspaceSlug, data);
      runInAction(() => {
        if (!this.dashboardPresets[workspaceSlug]) {
          this.dashboardPresets[workspaceSlug] = [];
        }
        this.dashboardPresets[workspaceSlug].push(response);
      });
      return response;
    } catch (error) {
      console.error("Failed to create dashboard preset", error);
      throw error;
    }
  };

  updateDashboardPreset = async (
    workspaceSlug: string,
    presetId: string,
    data: Partial<TDashboardPreset>
  ): Promise<TDashboardPreset> => {
    const originalPresets = { ...this.dashboardPresets };
    try {
      const response = await this.dashboardService.updateDashboardPreset(workspaceSlug, presetId, data);
      runInAction(() => {
        const index = this.dashboardPresets[workspaceSlug]?.findIndex((p) => p.id === presetId);
        if (index !== undefined && index !== -1) {
          this.dashboardPresets[workspaceSlug][index] = response;
        }
      });
      return response;
    } catch (error) {
      runInAction(() => {
        this.dashboardPresets = originalPresets;
      });
      console.error("Failed to update dashboard preset", error);
      throw error;
    }
  };

  deleteDashboardPreset = async (workspaceSlug: string, presetId: string): Promise<void> => {
    const originalPresets = [...(this.dashboardPresets[workspaceSlug] || [])];
    try {
      await this.dashboardService.deleteDashboardPreset(workspaceSlug, presetId);
      runInAction(() => {
        this.dashboardPresets[workspaceSlug] = this.dashboardPresets[workspaceSlug]?.filter((p) => p.id !== presetId);
        if (this.activeDashboardPresetId === presetId) {
          this.activeDashboardPresetId = null;
        }
      });
    } catch (error) {
      runInAction(() => {
        this.dashboardPresets[workspaceSlug] = originalPresets;
      });
      console.error("Failed to delete dashboard preset", error);
      throw error;
    }
  };

  setActiveDashboardPreset = (presetId: string | null) => {
    this.activeDashboardPresetId = presetId;
  };

  applyDashboardPreset = async (workspaceSlug: string, preset: TDashboardPreset): Promise<void> => {
    const dashboardId = this.homeDashboardId;
    if (!dashboardId) throw new Error("Dashboard not found");

    runInAction(() => {
      this.activeDashboardPresetId = preset.id;
    });

    const currentWidgets = this.widgetDetails[workspaceSlug]?.[dashboardId];
    if (!currentWidgets) return;

    const updatedWidgets = currentWidgets.map((widget) => {
      const presetWidget = preset.widgets.find((w) => w.widget_key === widget.key);
      if (presetWidget) {
        return {
          ...widget,
          is_visible: presetWidget.is_visible,
          filters: presetWidget.filters,
        };
      }
      return widget;
    });

    runInAction(() => {
      set(this.widgetDetails, [workspaceSlug, dashboardId], updatedWidgets);
    });
  };

  updateDashboardAccess = async (workspaceSlug: string, dashboardId: string, access: TDashboardAccess): Promise<void> => {
    try {
      await this.dashboardService.updateDashboardAccess(workspaceSlug, dashboardId, { access });
    } catch (error) {
      console.error("Failed to update dashboard access", error);
      throw error;
    }
  };

  shareDashboard = async (
    workspaceSlug: string,
    dashboardId: string,
    userIds: string[],
    permission: TDashboardPermission
  ): Promise<TDashboardSharee[]> => {
    try {
      const response = await this.dashboardService.shareDashboard(workspaceSlug, dashboardId, {
        user_ids: userIds,
        permission,
      });
      return response;
    } catch (error) {
      console.error("Failed to share dashboard", error);
      throw error;
    }
  };

  removeShare = async (workspaceSlug: string, dashboardId: string, shareeId: string): Promise<void> => {
    try {
      await this.dashboardService.removeShare(workspaceSlug, dashboardId, shareeId);
    } catch (error) {
      console.error("Failed to remove share", error);
      throw error;
    }
  };

  generateEmbedCode = async (workspaceSlug: string, dashboardId: string, allowEmbed: boolean): Promise<string> => {
    try {
      const response = await this.dashboardService.generateEmbedCode(workspaceSlug, dashboardId, {
        allow_embed: allowEmbed,
      });
      return response.embed_code;
    } catch (error) {
      console.error("Failed to generate embed code", error);
      throw error;
    }
  };

  getDashboardSharees = async (workspaceSlug: string, dashboardId: string): Promise<TDashboardSharee[]> => {
    try {
      const response = await this.dashboardService.getDashboardSharees(workspaceSlug, dashboardId);
      return response;
    } catch (error) {
      console.error("Failed to get dashboard sharees", error);
      throw error;
    }
  };
}
