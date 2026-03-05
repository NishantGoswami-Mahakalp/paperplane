/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { FC } from "react";
import { observer } from "mobx-react";
import { useTranslation } from "@plane/i18n";
import type { TWidget } from "@plane/types";
import { DragHandle, ToggleSwitch } from "@plane/ui";

type TProps = {
  widget: TWidget;
  isLastChild: boolean;
  handleDrop: any;
  handleToggleVisibility: (widgetId: string, isVisible: boolean) => void;
};

export const DashboardWidgetItem: FC<TProps> = observer((props) => {
  const { widget, isLastChild, handleToggleVisibility } = props;
  const { t } = useTranslation();

  const getWidgetTitle = (key: string): string => {
    const titles: Record<string, string> = {
      overview_stats: t("dashboard.widgets.overview_stats"),
      assigned_issues: t("dashboard.widgets.assigned_issues"),
      created_issues: t("dashboard.widgets.created_issues"),
      issues_by_state_groups: t("dashboard.widgets.issues_by_state_groups"),
      issues_by_priority: t("dashboard.widgets.issues_by_priority"),
      recent_activity: t("dashboard.widgets.recent_activity"),
      recent_projects: t("dashboard.widgets.recent_projects"),
      recent_collaborators: t("dashboard.widgets.recent_collaborators"),
    };
    return titles[key] || key;
  };

  return (
    <div
      className={`group flex items-center gap-3 rounded border border-onward-200 bg-onward-50 p-3 ${
        !isLastChild ? "mb-2" : ""
      }`}
    >
      <DragHandle />
      <div className="flex-1">
        <div className="text-sm font-medium">{getWidgetTitle(widget.key)}</div>
        <div className="text-xs text-onward-400">{widget.key}</div>
      </div>
      <ToggleSwitch
        value={widget.is_visible}
        onChange={(value: boolean) => handleToggleVisibility(widget.id, value)}
      />
    </div>
  );
});
