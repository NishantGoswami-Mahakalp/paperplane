/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { AreaChart } from "@plane/propel/charts/area-chart";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { TrendChartLoader } from "../loaders";
import { WidgetFilterDropdown } from "../widget-filter-dropdown";
import { DURATION_FILTER_OPTIONS, EDurationFilters } from "@plane/constants";

interface CumulativeFlowWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const CumulativeFlowWidget: React.FC<CumulativeFlowWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats, getWidgetDetails } = useDashboard();

  const widgetDetails = getWidgetDetails(workspaceSlug, dashboardId, "cumulative_flow");
  const duration = widgetDetails?.filters?.duration || EDurationFilters.LAST_30_DAYS;

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}-${duration}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "cumulative_flow",
        target_date: duration,
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "cumulative_flow");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((datum: any) => ({
      name: datum.date,
      backlog: datum.backlog,
      unstarted: datum.unstarted,
      started: datum.started,
      completed: datum.completed,
      cancelled: datum.cancelled,
      date: datum.date,
    }));
  }, [stats, data]);

  const areas = [
    {
      key: "backlog",
      label: "Backlog",
      fill: "#6B7280",
      fillOpacity: 1,
      stackId: "flow",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#6B7280",
      strokeOpacity: 1,
    },
    {
      key: "unstarted",
      label: "Unstarted",
      fill: "#F59E0B",
      fillOpacity: 1,
      stackId: "flow",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#F59E0B",
      strokeOpacity: 1,
    },
    {
      key: "started",
      label: "In Progress",
      fill: "#3B82F6",
      fillOpacity: 1,
      stackId: "flow",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#3B82F6",
      strokeOpacity: 1,
    },
    {
      key: "completed",
      label: "Completed",
      fill: "#198038",
      fillOpacity: 1,
      stackId: "flow",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#198038",
      strokeOpacity: 1,
    },
    {
      key: "cancelled",
      label: "Cancelled",
      fill: "#EF4444",
      fillOpacity: 1,
      stackId: "flow",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#EF4444",
      strokeOpacity: 1,
    },
  ];

  if (isLoading) return <TrendChartLoader />;

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex h-32 flex-col items-center justify-center gap-2">
        <span className="text-tertiary">No cumulative flow data available</span>
        <WidgetFilterDropdown
          widgetKey="cumulative_flow"
          widgetId={widgetId}
          workspaceSlug={workspaceSlug}
          dashboardId={dashboardId}
          options={DURATION_FILTER_OPTIONS}
          currentFilter={duration}
        />
      </div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary">Cumulative Flow</h3>
        <div className="flex items-center gap-2">
          <WidgetFilterDropdown
            widgetKey="cumulative_flow"
            widgetId={widgetId}
            workspaceSlug={workspaceSlug}
            dashboardId={dashboardId}
            options={DURATION_FILTER_OPTIONS}
            currentFilter={duration}
          />
        </div>
      </div>
      <div className="flex flex-1 items-center">
        <AreaChart
          className="h-[280px] w-full"
          data={chartData}
          areas={areas}
          xAxis={{
            key: "name",
            label: "Date",
          }}
          yAxis={{
            key: "count",
            label: "Issues",
            offset: -60,
            dx: -24,
          }}
          legend={{
            align: "left",
            verticalAlign: "bottom",
            layout: "horizontal",
            wrapperStyles: {
              justifyContent: "start",
              alignContent: "start",
              paddingLeft: "40px",
              paddingTop: "10px",
            },
          }}
        />
      </div>
      <div className="flex justify-center gap-4 border-t border-subtle pt-3">
        <div className="flex items-center gap-2">
          <div className="bg-gray-500 h-3 w-3 rounded-full" />
          <span className="text-xs text-tertiary">Backlog</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-amber-500 h-3 w-3 rounded-full" />
          <span className="text-xs text-tertiary">Unstarted</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-blue-500 h-3 w-3 rounded-full" />
          <span className="text-xs text-tertiary">In Progress</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-green-600 h-3 w-3 rounded-full" />
          <span className="text-xs text-tertiary">Completed</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-red-500 h-3 w-3 rounded-full" />
          <span className="text-xs text-tertiary">Cancelled</span>
        </div>
      </div>
    </div>
  );
});

export default CumulativeFlowWidget;
