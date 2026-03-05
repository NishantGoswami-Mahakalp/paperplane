/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { PieChart } from "@plane/propel/charts/pie-chart";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { WidgetLoader } from "../loaders";

interface IssuesByStatusWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const IssuesByStatusWidget: React.FC<IssuesByStatusWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats } = useDashboard();

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "issues_by_status",
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const stats = getWidgetStats(workspaceSlug, dashboardId, "issues_by_status");

  const chartData = useMemo(() => {
    const dataToUse = stats || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.map((item: any) => ({
      name: item.state_name,
      value: item.count,
      color: item.color,
      group: item.state_group,
    }));
  }, [stats, data]);

  const totalCount = useMemo(() => {
    return chartData.reduce((acc, item) => acc + item.value, 0);
  }, [chartData]);

  const pieData = useMemo(() => {
    return chartData.map((item) => ({
      name: item.name,
      value: item.value,
      fill: item.color,
    }));
  }, [chartData]);

  if (isLoading) return <WidgetLoader />;

  if (!chartData || chartData.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-tertiary">No issues by status data available</div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary">Issues by Status</h3>
      </div>
      <div className="flex flex-1 items-center justify-center">
        <div className="h-[280px] w-full max-w-[320px]">
          <PieChart
            data={pieData}
            dataKey="value"
            nameKey="name"
            cells={pieData.map((item) => ({ fill: item.fill }))}
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            showLabel
            showTooltip
            showLegend
            legendProps={{
              layout: "horizontal",
              verticalAlign: "bottom",
              align: "center",
            }}
          />
        </div>
      </div>
      <div className="flex justify-center border-t border-subtle pt-3">
        <div className="text-center">
          <span className="text-2xl font-semibold text-secondary">{totalCount}</span>
          <p className="text-xs text-tertiary">Total Issues</p>
        </div>
      </div>
    </div>
  );
});

export default IssuesByStatusWidget;
