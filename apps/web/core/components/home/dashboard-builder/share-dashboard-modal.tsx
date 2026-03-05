/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState, useEffect } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { useTranslation } from "@plane/i18n";
import { useDashboard } from "@/hooks/store/use-dashboard";
import { EDashboardAccess, EDashboardPermission } from "@plane/constants";
import type { TDashboardSharee } from "@plane/types";
import { Button, Input, ModalCore, EModalWidth, Avatar, ToggleSwitch } from "@plane/ui";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";

const ACCESS_OPTIONS = [
  { value: EDashboardAccess.PRIVATE, labelKey: "dashboard.share.visibility.private", descKey: "dashboard.share.visibility.private_description" },
  { value: EDashboardAccess.TEAMSPACE, labelKey: "dashboard.share.visibility.teamspace", descKey: "dashboard.share.visibility.teamspace_description" },
  { value: EDashboardAccess.WORKSPACE, labelKey: "dashboard.share.visibility.workspace", descKey: "dashboard.share.visibility.workspace_description" },
  { value: EDashboardAccess.PUBLIC, labelKey: "dashboard.share.visibility.public", descKey: "dashboard.share.visibility.public_description" },
];

const PERMISSION_OPTIONS = [
  { value: EDashboardPermission.VIEW, labelKey: "dashboard.share.permissions.view" },
  { value: EDashboardPermission.EDIT, labelKey: "dashboard.share.permissions.edit" },
  { value: EDashboardPermission.ADMIN, labelKey: "dashboard.share.permissions.admin" },
];

export const ShareDashboardModal = observer(function ShareDashboardModal({
  isOpen,
  onClose,
  dashboardId,
}: {
  isOpen: boolean;
  onClose: () => void;
  dashboardId?: string;
}) {
  const { workspaceSlug } = useParams();
  const { t } = useTranslation();
  const dashboardStore = useDashboard();
  const [access, setAccess] = useState<EDashboardAccess>(EDashboardAccess.PRIVATE);
  const [sharees, setSharees] = useState<TDashboardSharee[]>([]);
  const [embedCode, setEmbedCode] = useState<string>("");
  const [allowEmbed, setAllowEmbed] = useState(false);
  const [isCopied, setIsCopied] = useState(false);
  const [isEmbedCopied, setIsEmbedCopied] = useState(false);
  const [userEmail, setUserEmail] = useState("");
  const [selectedPermission, setSelectedPermission] = useState<EDashboardPermission>(EDashboardPermission.VIEW);
  const [isAddingUser, setIsAddingUser] = useState(false);

  useEffect(() => {
    if (isOpen && workspaceSlug && dashboardId) {
      Promise.all([
        dashboardStore.generateEmbedCode(workspaceSlug as string, dashboardId, false),
        dashboardStore.getDashboardSharees(workspaceSlug as string, dashboardId),
      ])
        .then(([code, shareesData]) => {
          setEmbedCode(code);
          setAllowEmbed(!!code);
          setSharees(shareesData || []);
        })
        .catch(() => {
          setEmbedCode("");
          setAllowEmbed(false);
          setSharees([]);
        });
    }
  }, [isOpen, workspaceSlug, dashboardId, dashboardStore]);

  const generateShareUrl = () => {
    if (!workspaceSlug) return "";
    const baseUrl = window.location.origin;
    return `${baseUrl}/${workspaceSlug}/dashboard?shared=true`;
  };

  const handleCopyLink = async () => {
    const url = generateShareUrl();
    try {
      await navigator.clipboard.writeText(url);
      setIsCopied(true);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.share.copied"),
      });
      setTimeout(() => setIsCopied(false), 2000);
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.share.copy_failed"),
      });
    }
  };

  const handleAccessChange = async (newAccess: EDashboardAccess) => {
    if (!workspaceSlug || !dashboardId) return;
    try {
      await dashboardStore.updateDashboardAccess(workspaceSlug as string, dashboardId, newAccess);
      setAccess(newAccess);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: "Dashboard visibility updated",
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: "Failed to update visibility",
      });
    }
  };

  const handleEmbedToggle = async () => {
    if (!workspaceSlug || !dashboardId) return;
    try {
      const newAllowEmbed = !allowEmbed;
      const code = await dashboardStore.generateEmbedCode(workspaceSlug as string, dashboardId, newAllowEmbed);
      setEmbedCode(code);
      setAllowEmbed(newAllowEmbed);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: newAllowEmbed ? "Embed enabled" : "Embed disabled",
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: "Failed to update embed settings",
      });
    }
  };

  const handleCopyEmbedCode = async () => {
    try {
      await navigator.clipboard.writeText(embedCode);
      setIsEmbedCopied(true);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: t("dashboard.share.embed.copied"),
      });
      setTimeout(() => setIsEmbedCopied(false), 2000);
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: t("dashboard.share.copy_failed"),
      });
    }
  };

  const handleRemoveShare = async (shareeId: string) => {
    if (!workspaceSlug || !dashboardId) return;
    try {
      await dashboardStore.removeShare(workspaceSlug as string, dashboardId, shareeId);
      setSharees(sharees.filter((s) => s.id !== shareeId));
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: "User removed from dashboard",
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: "Failed to remove user",
      });
    }
  };

  const handleAddUser = async () => {
    if (!workspaceSlug || !dashboardId || !userEmail.trim()) return;
    setIsAddingUser(true);
    try {
      const newSharees = await dashboardStore.shareDashboard(
        workspaceSlug as string,
        dashboardId,
        [userEmail.trim()],
        selectedPermission
      );
      setSharees([...sharees, ...newSharees]);
      setUserEmail("");
      setSelectedPermission(EDashboardPermission.VIEW);
      setToast({
        type: TOAST_TYPE.SUCCESS,
        title: t("toast.success"),
        message: "User added to dashboard",
      });
    } catch {
      setToast({
        type: TOAST_TYPE.ERROR,
        title: t("toast.error"),
        message: "Failed to add user",
      });
    } finally {
      setIsAddingUser(false);
    }
  };

  return (
    <ModalCore isOpen={isOpen} handleClose={onClose} width={EModalWidth.MD}>
      <div className="p-4 space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-1">{t("dashboard.share.title")}</h3>
          <p className="text-sm text-onward-500">{t("dashboard.share.description")}</p>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium">{t("dashboard.share.visibility.title")}</label>
          <div className="grid grid-cols-2 gap-2">
            {ACCESS_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => handleAccessChange(option.value as EDashboardAccess)}
                className={`p-3 text-left rounded-md border transition-colors ${
                  access === option.value
                    ? "border-primary bg-primary/5"
                    : "border-onward-200 hover:border-onward-300"
                }`}
              >
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{t(option.labelKey)}</span>
                </div>
                <p className="text-xs text-onward-500 mt-1">{t(option.descKey)}</p>
              </button>
            ))}
          </div>
        </div>

        <div className="space-y-3">
          <label className="text-sm font-medium">{t("dashboard.share.share_with")}</label>
          <div className="flex gap-2">
            <Input
              value={generateShareUrl()}
              className="flex-1"
              readOnly
            />
            <Button variant="primary" onClick={handleCopyLink}>
              {isCopied ? t("dashboard.share.copied") : t("dashboard.share.copy")}
            </Button>
          </div>

          <div className="flex gap-2 mt-3">
            <Input
              value={userEmail}
              onChange={(e) => setUserEmail(e.target.value)}
              placeholder="Enter user email"
              className="flex-1"
            />
            <select
              className="px-3 py-2 border border-onward-200 rounded-md text-sm"
              value={selectedPermission}
              onChange={(e) => setSelectedPermission(e.target.value as EDashboardPermission)}
            >
              {PERMISSION_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {t(opt.labelKey)}
                </option>
              ))}
            </select>
            <Button
              variant="primary"
              onClick={handleAddUser}
              disabled={!userEmail.trim() || isAddingUser}
            >
              {t("dashboard.share.add_users")}
            </Button>
          </div>

          {sharees.length > 0 && (
            <div className="space-y-2 mt-3">
              {sharees.map((sharee) => (
                <div key={sharee.id} className="flex items-center justify-between p-2 bg-onward-50 rounded-md">
                  <div className="flex items-center gap-2">
                    <Avatar name={sharee.user_id} />
                    <span className="text-sm">{sharee.user_id}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-onward-500">
                      {t(`dashboard.share.permissions.${sharee.permission}`)}
                    </span>
                    <Button variant="tertiary-danger" size="sm" onClick={() => handleRemoveShare(sharee.id)}>
                      {t("dashboard.share.remove")}
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="space-y-3 pt-3 border-t border-onward-200">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium">{t("dashboard.share.embed.title")}</label>
            <ToggleSwitch value={allowEmbed} onChange={handleEmbedToggle} />
          </div>
          {allowEmbed && embedCode && (
            <div className="flex gap-2">
              <Input
                value={embedCode}
                className="flex-1 font-mono text-xs"
                readOnly
              />
              <Button variant="primary" onClick={handleCopyEmbedCode}>
                {isEmbedCopied ? t("dashboard.share.embed.copied") : t("dashboard.share.embed.copy_code")}
              </Button>
            </div>
          )}
        </div>

        <div className="flex justify-end pt-2">
          <Button variant="neutral-primary" onClick={onClose}>
            {t("common.close")}
          </Button>
        </div>
      </div>
    </ModalCore>
  );
});
