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

interface IssuesTrendWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const IssuesTrendWidget: React.FC<IssuesTrendWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats } = useDashboard();

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "issues_trend",
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "issues_trend");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((datum: any) => ({
      name: datum.date,
      created: datum.created,
      resolved: datum.resolved,
      date: datum.date,
    }));
  }, [stats, data]);

  const areas = [
    {
      key: "created",
      label: "Created",
      fill: "#1192E833",
      fillOpacity: 1,
      stackId: "trend-one",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#1192E8",
      strokeOpacity: 1,
    },
    {
      key: "resolved",
      label: "Resolved",
      fill: "#19803833",
      fillOpacity: 1,
      stackId: "trend-one",
      showDot: false,
      smoothCurves: true,
      strokeColor: "#198038",
      strokeOpacity: 1,
    },
  ];

  const totalCreated = useMemo(() => {
    return chartData.reduce((acc, item) => acc + item.created, 0);
  }, [chartData]);

  const totalResolved = useMemo(() => {
    return chartData.reduce((acc, item) => acc + item.resolved, 0);
  }, [chartData]);

  if (isLoading) return <TrendChartLoader />;

  if (!chartData || chartData.length === 0) {
    return <div className="flex h-32 items-center justify-center text-tertiary">No trend data available</div>;
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary">Issues Trend</h3>
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
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-[#1192E8]" />
          <span className="text-sm text-secondary">Created: {totalCreated}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="h-3 w-3 rounded-full bg-[#198038]" />
          <span className="text-sm text-secondary">Resolved: {totalResolved}</span>
        </div>
      </div>
    </div>
  );
});

export default IssuesTrendWidget;
