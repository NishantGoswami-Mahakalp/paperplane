/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { DragLocationHistory, DropTargetRecord, ElementDragPayload } from "@atlaskit/pragmatic-drag-and-drop/dist/types/internal-types";
import { observer } from "mobx-react";
import { useTranslation } from "@plane/i18n";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { DashboardWidgetItem } from "./widget-item";

type TTargetData = {
  id: string;
  widgetKey: string;
  isChild: boolean;
};

const getInstructionFromPayload = (
  dropTarget: DropTargetRecord,
  _source: ElementDragPayload,
  _location: DragLocationHistory
): string | undefined => {
  const instruction = dropTarget?.data?.instruction as string | undefined;
  return instruction;
};

export const DashboardWidgetsList = observer(function DashboardWidgetsList({
  workspaceSlug,
}: {
  workspaceSlug: string;
}) {
  const { t } = useTranslation();
  const { homeDashboardWidgets, homeDashboardId, updateDashboardWidget } = useDashboard();
  const widgets = homeDashboardWidgets || [];

  const handleDrop = async (
    self: DropTargetRecord,
    source: ElementDragPayload,
    location: DragLocationHistory
  ) => {
    const dropTargets = location?.current?.dropTargets ?? [];
    if (!dropTargets || dropTargets.length <= 0) return;
    const dropTarget =
      dropTargets.length > 1 ? dropTargets.find((target: DropTargetRecord) => target?.data?.isChild) : dropTargets[0];

    const dropTargetData = dropTarget?.data as TTargetData;

    if (!dropTarget || !dropTargetData) return;
    getInstructionFromPayload(dropTarget, source, location);
    const droppedId = dropTargetData.id;
    const sourceData = source.data as TTargetData;

    if (!sourceData.id || !homeDashboardId) return;

    const sourceWidget = widgets.find((w) => w.id === sourceData.id);
    const targetWidget = widgets.find((w) => w.id === droppedId);

    if (!sourceWidget || !targetWidget) return;

    const sourceIndex = widgets.findIndex((w) => w.id === sourceData.id);
    const targetIndex = widgets.findIndex((w) => w.id === droppedId);

    const reorderedWidgets = [...widgets];
    reorderedWidgets.splice(sourceIndex, 1);
    reorderedWidgets.splice(targetIndex, 0, sourceWidget);

    try {
      await updateDashboardWidget(workspaceSlug, homeDashboardId, sourceWidget.id, {
        sort_order: targetIndex,
      } as any);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.widget.reordered_successfully"),
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.widget.reordering_failed"),
      });
    }
  };

  const handleToggleVisibility = async (widgetId: string, isVisible: boolean) => {
    if (!homeDashboardId) return;
    try {
      await updateDashboardWidget(workspaceSlug, homeDashboardId, widgetId, {
        is_visible: isVisible,
      });
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: isVisible ? t("dashboard.widget.shown") : t("dashboard.widget.hidden"),
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.widget.toggle_failed"),
      });
    }
  };

  return (
    <div className="my-4">
      <div className="text-sm text-onward-500 mb-2">{t("dashboard.builder.drag_to_reorder")}</div>
      {widgets.map((widget, index) => (
        <DashboardWidgetItem
          key={widget.id}
          widget={widget}
          isLastChild={index === widgets.length - 1}
          handleDrop={handleDrop}
          handleToggleVisibility={handleToggleVisibility}
        />
      ))}
    </div>
  );
});
