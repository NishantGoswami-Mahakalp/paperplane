/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { LineChart } from "@plane/propel/charts/line-chart";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { TrendChartLoader } from "../loaders";
import { WidgetFilterDropdown } from "../widget-filter-dropdown";
import { DURATION_FILTER_OPTIONS, EDurationFilters } from "@plane/constants";

interface CycleTimeWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const CycleTimeWidget: React.FC<CycleTimeWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats, getWidgetDetails } = useDashboard();

  const widgetDetails = getWidgetDetails(workspaceSlug, dashboardId, "cycle_time");
  const duration = widgetDetails?.filters?.duration || EDurationFilters.LAST_30_DAYS;

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}-${duration}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "cycle_time",
        target_date: duration,
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "cycle_time");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((datum: any) => ({
      name: datum.date,
      cycleTime: datum.avg_cycle_time,
      date: datum.date,
    }));
  }, [stats, data]);

  const avgCycleTime = useMemo(() => {
    if (chartData.length === 0) return 0;
    const totalCycleTime = chartData.reduce((acc, item) => acc + item.cycleTime, 0);
    return (totalCycleTime / chartData.length).toFixed(1);
  }, [chartData]);

  const totalIssues = useMemo(() => {
    if (!stats && !data) return 0;
    const dataToUse = stats || data;
    if (!Array.isArray(dataToUse)) return 0;
    return dataToUse.reduce((acc: number, item: any) => acc + (item.issues_count || 0), 0);
  }, [stats, data]);

  if (isLoading) return <TrendChartLoader />;

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex h-32 flex-col items-center justify-center gap-2">
        <span className="text-tertiary">No cycle time data available</span>
        <WidgetFilterDropdown
          widgetKey="cycle_time"
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
        <h3 className="text-lg font-semibold text-secondary">Cycle Time</h3>
        <div className="flex items-center gap-2">
          <WidgetFilterDropdown
            widgetKey="cycle_time"
            widgetId={widgetId}
            workspaceSlug={workspaceSlug}
            dashboardId={dashboardId}
            options={DURATION_FILTER_OPTIONS}
            currentFilter={duration}
          />
        </div>
      </div>
      <div className="flex flex-1 items-center">
        <LineChart
          className="h-[280px] w-full"
          data={chartData}
          lines={[
            {
              key: "cycleTime",
              label: "Cycle Time (days)",
              stroke: "#9D4EDD",
              fill: "#9D4EDD33",
              dashedLine: false,
              showDot: true,
              smoothCurves: true,
            },
          ]}
          xAxis={{
            key: "name",
            label: "Date",
          }}
          yAxis={{
            key: "count",
            label: "Days",
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
      <div className="flex justify-center gap-8 border-t border-subtle pt-3">
        <div className="flex flex-col items-center">
          <span className="text-lg font-semibold text-secondary">{avgCycleTime}</span>
          <span className="text-xs text-tertiary">Avg Cycle Time (days)</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-lg text-purple-600 font-semibold">{totalIssues}</span>
          <span className="text-xs text-tertiary">Total Issues</span>
        </div>
      </div>
    </div>
  );
});

export default CycleTimeWidget;
