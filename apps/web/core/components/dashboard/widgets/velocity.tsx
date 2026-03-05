/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { BarChart } from "@plane/propel/charts/bar-chart";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { TrendChartLoader } from "../loaders";
import { WidgetFilterDropdown } from "../widget-filter-dropdown";
import { DURATION_FILTER_OPTIONS, EDurationFilters } from "@plane/constants";

interface VelocityWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const VelocityWidget: React.FC<VelocityWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats, getWidgetDetails } = useDashboard();

  const widgetDetails = getWidgetDetails(workspaceSlug, dashboardId, "velocity");
  const duration = widgetDetails?.filters?.duration || EDurationFilters.LAST_30_DAYS;
  const segmentBy = widgetDetails?.filters?.segment_by || "week";

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}-${duration}-${segmentBy}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "velocity",
        target_date: duration,
        segment_by: segmentBy as "week" | "month",
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "velocity");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((datum: any) => ({
      name: datum.date,
      completed: datum.completed,
      date: datum.date,
    }));
  }, [stats, data]);

  const totalCompleted = useMemo(() => {
    return chartData.reduce((acc, item) => acc + item.completed, 0);
  }, [chartData]);

  const avgVelocity = useMemo(() => {
    if (chartData.length === 0) return 0;
    return Math.round(totalCompleted / chartData.length);
  }, [chartData, totalCompleted]);

  if (isLoading) return <TrendChartLoader />;

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex h-32 flex-col items-center justify-center gap-2">
        <span className="text-tertiary">No velocity data available</span>
        <WidgetFilterDropdown
          widgetKey="velocity"
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
        <h3 className="text-lg font-semibold text-secondary">Velocity</h3>
        <div className="flex items-center gap-2">
          <WidgetFilterDropdown
            widgetKey="velocity"
            widgetId={widgetId}
            workspaceSlug={workspaceSlug}
            dashboardId={dashboardId}
            options={DURATION_FILTER_OPTIONS}
            currentFilter={duration}
          />
        </div>
      </div>
      <div className="flex flex-1 items-center">
        <BarChart
          className="h-[280px] w-full"
          data={chartData}
          bars={[
            {
              key: "completed",
              label: "Completed",
              fill: "#198038",
              textClassName: "fill-custom-text-300",
              stackId: "velocity",
            },
          ]}
          xAxis={{
            key: "name",
            label: segmentBy === "week" ? "Week" : "Month",
          }}
          yAxis={{
            key: "count",
            label: "Issues",
            offset: -60,
            dx: -24,
          }}
          barSize={40}
        />
      </div>
      <div className="flex justify-center gap-8 border-t border-subtle pt-3">
        <div className="flex flex-col items-center">
          <span className="text-lg font-semibold text-secondary">{totalCompleted}</span>
          <span className="text-xs text-tertiary">Total Completed</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-lg text-green-600 font-semibold">{avgVelocity}</span>
          <span className="text-xs text-tertiary">Avg per {segmentBy}</span>
        </div>
      </div>
    </div>
  );
});

export default VelocityWidget;
