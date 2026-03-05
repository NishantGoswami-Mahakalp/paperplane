/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo } from "react";
import { observer } from "mobx-react";
import useSWR from "swr";
import { Avatar } from "@plane/ui";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { WidgetCardLoader } from "../loaders";

const getLoadColor = (count: number): string => {
  if (count === 0) return "text-tertiary";
  if (count <= 3) return "text-green-600";
  if (count <= 6) return "text-yellow-600";
  return "text-red-600";
};

const getLoadLabel = (count: number): string => {
  if (count === 0) return "No issues";
  if (count <= 3) return "Low";
  if (count <= 6) return "Medium";
  return "High";
};

interface AssigneeWorkloadWidgetProps {
  workspaceSlug: string;
  dashboardId: string;
  widgetId: string;
}

const AssigneeWorkloadWidget: React.FC<AssigneeWorkloadWidgetProps> = observer((props) => {
  const { workspaceSlug, dashboardId, widgetId } = props;
  const { getWidgetStats, fetchWidgetStats } = useDashboard();

  const swrKey = `dashboard-widget-${widgetId}-${workspaceSlug}-${dashboardId}`;
  const { data, isLoading } = useSWR(
    swrKey,
    () =>
      fetchWidgetStats(workspaceSlug, dashboardId, {
        widget_key: "assignee_workload",
      }),
    {
      revalidateOnFocus: false,
      dedupingInterval: 60000,
    }
  );

  const workloadData = useMemo(() => {
    const dataToUse = getWidgetStats(workspaceSlug, dashboardId, "assignee_workload") || data;
    if (!dataToUse || !Array.isArray(dataToUse)) return [];
    return dataToUse.toSorted((a: any, b: any) => b.total_issues - a.total_issues).slice(0, 5);
  }, [data, workspaceSlug, dashboardId, getWidgetStats]);

  if (isLoading) {
    return (
      <div className="flex flex-col gap-3">
        <WidgetCardLoader />
        <WidgetCardLoader />
        <WidgetCardLoader />
      </div>
    );
  }

  if (!workloadData || workloadData.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center text-tertiary">No assignee workload data available</div>
    );
  }

  return (
    <div className="flex h-full w-full flex-col gap-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-secondary">Assignee Workload</h3>
      </div>
      <div className="flex flex-col gap-3">
        {workloadData.map((assignee: any) => (
          <div
            key={assignee.assignee_id}
            className="flex items-center justify-between rounded-md border border-subtle p-3"
          >
            <div className="flex items-center gap-3">
              {assignee.assignee_avatar ? (
                <Avatar src={assignee.assignee_avatar} name={assignee.assignee_name} size="md" />
              ) : (
                <Avatar name={assignee.assignee_name} size="md" />
              )}
              <div className="flex flex-col">
                <span className="text-sm font-medium text-secondary">{assignee.assignee_name}</span>
                <span className={`text-xs ${getLoadColor(assignee.total_issues)}`}>
                  {getLoadLabel(assignee.total_issues)}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="flex flex-col items-center">
                <span className="text-lg font-semibold text-secondary">{assignee.total_issues}</span>
                <span className="text-xs text-tertiary">Total</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-lg text-blue-600 font-semibold">{assignee.in_progress_issues}</span>
                <span className="text-xs text-tertiary">In Progress</span>
              </div>
              <div className="flex flex-col items-center">
                <span className="text-lg text-green-600 font-semibold">{assignee.completed_issues}</span>
                <span className="text-xs text-tertiary">Completed</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
});

export default AssigneeWorkloadWidget;
