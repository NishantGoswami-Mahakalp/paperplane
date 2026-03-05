/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useCallback, useMemo, useState } from "react";
import useSWR from "swr";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { dashboardQueryBuilder } from "@/services/dashboard/dashboard-query-builder";
import type { TWidgetKeys, TWidgetStatsResponse, TWidgetStatsRequestParams } from "@plane/types";

interface UseDashboardWidgetOptions {
  widgetKey: TWidgetKeys;
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
  filters?: {
    duration?: string;
    custom_dates?: string[];
    project_ids?: string[];
    assignees?: string[];
    segment_by?: "state_group" | "priority" | "assignee";
    cycle_id?: string;
    plot_type?: "burndown" | "burnup";
  };
  options?: {
    revalidateOnFocus?: boolean;
    dedupingInterval?: number;
    refreshInterval?: number;
  };
}

export const useDashboardWidget = <T extends TWidgetStatsResponse>({
  widgetKey,
  workspaceSlug,
  dashboardId,
  widgetId,
  filters,
  options,
}: UseDashboardWidgetOptions) => {
  const { fetchWidgetStats, getWidgetStats } = useDashboard();

  const queryParams = useMemo(() => {
    return dashboardQueryBuilder.buildQuery(widgetKey, {
      widgetKey,
      filters: filters as any,
    });
  }, [widgetKey, filters]);

  const swrKey = useMemo(
    () => `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}-${widgetKey}`,
    [widgetId, workspaceSlug, dashboardId, widgetKey]
  );

  const { data, isLoading, error, mutate } = useSWR(
    swrKey,
    () => fetchWidgetStats(workspaceSlug, dashboardId, queryParams as TWidgetStatsRequestParams),
    {
      revalidateOnFocus: options?.revalidateOnFocus ?? false,
      dedupingInterval: options?.dedupingInterval ?? 60000,
      refreshInterval: options?.refreshInterval,
    }
  );

  const cachedStats = getWidgetStats<T>(workspaceSlug, dashboardId, widgetKey);

  const refresh = useCallback(() => {
    mutate();
  }, [mutate]);

  return {
    data: (cachedStats as T) || data,
    isLoading,
    error,
    refresh,
    queryParams,
  };
};

export const useDashboardCache = () => {
  const [cache, setCache] = useState<Record<string, { data: any; timestamp: number }>>({});

  const getCached = useCallback(
    (key: string, maxAge: number = 300000) => {
      const cached = cache[key];
      if (cached && Date.now() - cached.timestamp < maxAge) {
        return cached.data;
      }
      return null;
    },
    [cache]
  );

  const setCached = useCallback((key: string, data: any) => {
    setCache((prev) => ({
      ...prev,
      [key]: { data, timestamp: Date.now() },
    }));
  }, []);

  const clearCache = useCallback(() => {
    setCache({});
  }, []);

  return {
    getCached,
    setCached,
    clearCache,
  };
};
