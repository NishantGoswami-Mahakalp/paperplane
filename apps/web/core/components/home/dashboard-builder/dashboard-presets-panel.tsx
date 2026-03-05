/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { useTranslation } from "@plane/i18n";
import { Button, Input, ModalCore, EModalWidth, ToggleSwitch } from "@plane/ui";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";
import { useDashboard } from "@/hooks/store/use-dashboard";

export const DashboardPresetsPanel = observer(function DashboardPresetsPanel() {
  const { workspaceSlug } = useParams();
  const { t } = useTranslation();
  const {
    dashboardPresets,
    activeDashboardPresetId,
    homeDashboardWidgets,
    homeDashboardId,
    createDashboardPreset,
    deleteDashboardPreset,
    setActiveDashboardPreset,
    applyDashboardPreset,
  } = useDashboard();

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newPresetName, setNewPresetName] = useState("");
  const [newPresetDescription, setNewPresetDescription] = useState("");
  const [newPresetIsGlobal, setNewPresetIsGlobal] = useState(false);

  const presets = workspaceSlug ? dashboardPresets[workspaceSlug.toString()] || [] : [];

  const handleCreatePreset = async () => {
    if (!workspaceSlug || !newPresetName.trim() || !homeDashboardId || !homeDashboardWidgets) return;

    try {
      const widgetsData = homeDashboardWidgets.map((widget) => ({
        widget_id: widget.id,
        widget_key: widget.key,
        is_visible: widget.is_visible,
        sort_order: 0,
        filters: widget.filters,
      }));

      await createDashboardPreset(workspaceSlug.toString(), {
        name: newPresetName.trim(),
        description: newPresetDescription.trim(),
        is_global: newPresetIsGlobal,
        widgets: widgetsData,
      });
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.dashboard_preset.created"),
      });
      setIsCreateModalOpen(false);
      setNewPresetName("");
      setNewPresetDescription("");
      setNewPresetIsGlobal(false);
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.dashboard_preset.create_failed"),
      });
    }
  };

  const handleDeletePreset = async (presetId: string) => {
    if (!workspaceSlug) return;

    try {
      await deleteDashboardPreset(workspaceSlug.toString(), presetId);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.dashboard_preset.deleted"),
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.dashboard_preset.delete_failed"),
      });
    }
  };

  const handleApplyPreset = async (preset: any) => {
    if (!workspaceSlug) return;

    try {
      await applyDashboardPreset(workspaceSlug.toString(), preset);
      setActiveDashboardPreset(preset.id);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.dashboard_preset.applied"),
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.dashboard_preset.apply_failed"),
      });
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">{t("dashboard.dashboard_presets.title")}</h3>
        <Button variant="primary" size="sm" onClick={() => setIsCreateModalOpen(true)}>
          {t("dashboard.dashboard_presets.save")}
        </Button>
      </div>

      <div className="space-y-2">
        {presets.length === 0 ? (
          <div className="text-center py-8 text-onward-400">
            {t("dashboard.dashboard_presets.empty")}
          </div>
        ) : (
          presets.map((preset) => (
            <div
              key={preset.id}
              className={`flex items-center justify-between p-3 rounded border ${
                activeDashboardPresetId === preset.id
                  ? "border-accent-primary bg-accent-primary/10"
                  : "border-onward-200 bg-onward-50"
              }`}
            >
              <div className="flex-1">
                <div className="font-medium">{preset.name}</div>
                {preset.description && (
                  <div className="text-xs text-onward-400">{preset.description}</div>
                )}
                <div className="text-xs text-onward-400 mt-1">
                  {preset.widgets.length} {t("dashboard.dashboard_presets.widgets")}
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="accent-primary" size="sm" onClick={() => handleApplyPreset(preset)}>
                  {t("dashboard.dashboard_presets.apply")}
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeletePreset(preset.id);
                  }}
                >
                  {t("common.delete")}
                </Button>
              </div>
            </div>
          ))
        )}
      </div>

      <ModalCore
        isOpen={isCreateModalOpen}
        handleClose={() => setIsCreateModalOpen(false)}
        width={EModalWidth.SM}
      >
        <div className="p-4">
          <h3 className="text-lg font-semibold mb-4">{t("dashboard.dashboard_presets.save_as")}</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                {t("dashboard.dashboard_presets.name")}
              </label>
              <Input
                value={newPresetName}
                onChange={(e) => setNewPresetName(e.target.value)}
                placeholder={t("dashboard.dashboard_presets.name_placeholder")}
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                {t("dashboard.dashboard_presets.description")}
              </label>
              <Input
                value={newPresetDescription}
                onChange={(e) => setNewPresetDescription(e.target.value)}
                placeholder={t("dashboard.dashboard_presets.description_placeholder")}
              />
            </div>
            <div className="flex items-center gap-2">
              <ToggleSwitch
                value={newPresetIsGlobal}
                onChange={setNewPresetIsGlobal}
              />
              <span className="text-sm">{t("dashboard.dashboard_presets.global")}</span>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="neutral-primary" onClick={() => setIsCreateModalOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button variant="primary" onClick={handleCreatePreset}>
                {t("common.save")}
              </Button>
            </div>
          </div>
        </div>
      </ModalCore>
    </div>
  );
});
