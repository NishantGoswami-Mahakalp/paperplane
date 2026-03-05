/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { Plus } from "lucide-react";
import { observer } from "mobx-react";
import { useTranslation } from "@plane/i18n";
import { Button } from "@plane/ui";

type TIssueActivityWorklogCreateButton = {
  workspaceSlug: string;
  projectId: string;
  issueId: string;
  disabled: boolean;
};

export const IssueActivityWorklogCreateButton = observer(function IssueActivityWorklogCreateButton({
  workspaceSlug: _workspaceSlug,
  projectId: _projectId,
  issueId: _issueId,
  disabled,
}: TIssueActivityWorklogCreateButton) {
  const { t } = useTranslation();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleClick = () => {
    setIsModalOpen(true);
  };

  return (
    <>
      <Button
        variant="outline-primary"
        size="sm"
        prependIcon={<Plus className="h-3.5 w-3.5" />}
        onClick={handleClick}
        disabled={disabled}
      >
        {t("common.addWorklog")}
      </Button>
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="shadow-lg w-full max-w-md rounded-lg bg-surface-1 p-4">
            <h3 className="text-lg font-medium">{t("common.addWorklog")}</h3>
            <p className="text-sm text-text-secondary mt-2">
              Worklog creation form will be implemented with API integration.
            </p>
            <div className="mt-4 flex justify-end gap-2">
              <Button variant="outline-primary" onClick={() => setIsModalOpen(false)}>
                {t("common.cancel")}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
});
