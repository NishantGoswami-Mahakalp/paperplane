/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { useTranslation } from "@plane/i18n";
import { Button, Input, ModalCore, EModalWidth } from "@plane/ui";
import { TOAST_TYPE, setToast } from "@plane/propel/toast";

export const ShareDashboardModal = observer(function ShareDashboardModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const { workspaceSlug } = useParams();
  const { t } = useTranslation();
  const [shareUrl, setShareUrl] = useState("");
  const [isCopied, setIsCopied] = useState(false);

  const generateShareUrl = () => {
    if (!workspaceSlug) return "";
    const baseUrl = window.location.origin;
    return `${baseUrl}/${workspaceSlug}/dashboard?shared=true`;
  };

  const handleCopyLink = async () => {
    const url = generateShareUrl();
    try {
      await navigator.clipboard.writeText(url);
      setShareUrl(url);
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

  return (
    <ModalCore isOpen={isOpen} handleClose={onClose} width={EModalWidth.SM}>
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-4">{t("dashboard.share.title")}</h3>
        <div className="space-y-4">
          <p className="text-sm text-onward-500">{t("dashboard.share.description")}</p>
          <div className="flex gap-2">
            <Input
              value={shareUrl || generateShareUrl()}
              onChange={(e) => setShareUrl(e.target.value)}
              className="flex-1"
              readOnly
            />
            <Button variant="primary" onClick={handleCopyLink}>
              {isCopied ? t("dashboard.share.copied") : t("dashboard.share.copy")}
            </Button>
          </div>
          <div className="flex justify-end">
            <Button variant="neutral-primary" onClick={onClose}>
              {t("common.close")}
            </Button>
          </div>
        </div>
      </div>
    </ModalCore>
  );
});
