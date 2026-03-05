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

interface CycleBurndownWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const CycleBurndownWidget: React.FC<CycleBurndownWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats } = useDashboard();

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "cycle_burndown",
        cycle_id: "",
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "cycle_burndown");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((datum: any) => ({
      name: datum.date,
      remaining: datum.remaining,
      completed: datum.completed,
      total: datum.total,
      date: datum.date,
    }));
  }, [stats, data]);

  const lines = [
    {
      key: "remaining",
      label: "Remaining",
      stroke: "#1192E8",
      fill: "#1192E833",
      dashedLine: false,
      showDot: false,
      smoothCurves: true,
    },
    {
      key: "completed",
      label: "Completed",
      stroke: "#198038",
      fill: "#19803833",
      dashedLine: false,
      showDot: false,
      smoothCurves: true,
    },
  ];

  const totalIssues = useMemo(() => {
    if (!chartData || chartData.length === 0) return 0;
    return chartData[0]?.total || 0;
  }, [chartData]);

  const completedIssues = useMemo(() => {
    if (!chartData || chartData.length === 0) return 0;
    return chartData[chartData.length - 1]?.completed || 0;
  }, [chartData]);

  const remainingIssues = useMemo(() => {
    if (!chartData || chartData.length === 0) return 0;
    return chartData[chartData.length - 1]?.remaining || 0;
  }, [chartData]);

  const progressPercentage = useMemo(() => {
    if (totalIssues === 0) return 0;
    return Math.round((completedIssues / totalIssues) * 100);
  }, [totalIssues, completedIssues]);

  if (isLoading) return <TrendChartLoader />;

  if (!chartData || chartData.length === 0) {
    return <div className="flex h-32 items-center justify-center text-tertiary">No cycle burndown data available</div>;
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary">Cycle Burndown</h3>
        <div className="flex items-center gap-2">
          <span className="text-sm text-tertiary">Progress:</span>
          <span className="text-sm font-semibold text-secondary">{progressPercentage}%</span>
        </div>
      </div>
      <div className="flex flex-1 items-center">
        <LineChart
          className="h-[280px] w-full"
          data={chartData}
          lines={lines}
          xAxis={{
            key: "name",
            label: "Date",
          }}
          yAxis={{
            key: "count",
            label: "Count",
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
          <span className="text-lg font-semibold text-secondary">{totalIssues}</span>
          <span className="text-xs text-tertiary">Total</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-lg text-green-600 font-semibold">{completedIssues}</span>
          <span className="text-xs text-tertiary">Completed</span>
        </div>
        <div className="flex flex-col items-center">
          <span className="text-lg text-blue-600 font-semibold">{remainingIssues}</span>
          <span className="text-xs text-tertiary">Remaining</span>
        </div>
      </div>
    </div>
  );
});

export default CycleBurndownWidget;
