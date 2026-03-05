/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useCallback, useMemo, useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
// i18n
import { useTranslation } from "@plane/i18n";
// types
import type { TSelectionHelper } from "@/hooks/use-multiple-select";
import type { TBulkOperationsPayload, TBulkIssueProperties } from "@plane/types";
import { EIssuesStoreType } from "@plane/types";
// hooks
import { useMultipleSelectStore } from "@/hooks/store/use-multiple-select-store";
import { useIssues } from "@/hooks/store/use-issues";
import { useProjectState } from "@/hooks/store/use-project-state";
import { useUser } from "@/hooks/store/user";
// components
import { Button } from "@plane/ui";
import { cn } from "@plane/utils";
// modals
import { BulkDeleteIssuesModal } from "@/components/core/modals/bulk-delete-issues-modal";

type Props = {
  className?: string;
  selectionHelpers: TSelectionHelper;
};

export const IssueBulkOperationsRoot = observer(function IssueBulkOperationsRoot(props: Props) {
  const { className, selectionHelpers } = props;
  // router
  const params = useParams();
  const workspaceSlug = params?.workspaceSlug as string;
  const projectId = params?.projectId as string;
  // store hooks
  const { isSelectionActive, selectedEntityIds } = useMultipleSelectStore();
  const projectState = useProjectState();
  const issuesStore = useIssues(EIssuesStoreType.PROJECT);
  const { data: user } = useUser();
  // i18n
  const { t } = useTranslation();
  // state
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isUpdating, setIsUpdating] = useState(false);

  const selectedIssues = useMemo(() => {
    const ids: string[] = [];
    selectedEntityIds.forEach((entityId) => {
      const parts = entityId.split("__");
      const issueId = parts.length > 1 ? parts[1] : parts[0];
      if (issueId) ids.push(issueId);
    });
    return ids;
  }, [selectedEntityIds]);

  const handleBulkUpdate = useCallback(
    async (properties: Partial<TBulkIssueProperties>) => {
      if (!workspaceSlug || !projectId || selectedIssues.length === 0) return;

      setIsUpdating(true);
      try {
        const payload: TBulkOperationsPayload = {
          issue_ids: selectedIssues,
          properties,
        };
        await issuesStore.issues.bulkUpdateProperties(workspaceSlug, projectId, payload);
        selectionHelpers.handleClearSelection();
      } catch (error) {
        console.error("Error bulk updating issues:", error);
      } finally {
        setIsUpdating(false);
      }
    },
    [workspaceSlug, projectId, selectedIssues, issuesStore, selectionHelpers]
  );

  const handleDelete = useCallback(() => {
    setShowDeleteModal(true);
  }, []);

  if (!isSelectionActive || selectionHelpers.isSelectionDisabled) return null;

  const states = projectState.projectStates || [];
  const priorities = [
    { value: "urgent", label: t("priority.urgent") },
    { value: "high", label: t("priority.high") },
    { value: "medium", label: t("priority.medium") },
    { value: "low", label: t("priority.low") },
    { value: "none", label: t("priority.none") },
  ];

  return (
    <>
      <div
        className={cn(
          "sticky bottom-0 left-0 z-[2] flex h-14 w-full items-center justify-between gap-2 border-t border-border-primary bg-surface-1 px-4",
          className
        )}
      >
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-text-secondary">
            {selectedIssues.length} {selectedIssues.length === 1 ? "item" : "items"} selected
          </span>
          <Button
            variant="link-neutral"
            size="sm"
            onClick={() => selectionHelpers.handleClearSelection()}
            className="text-text-secondary hover:text-text-primary"
          >
            {t("common.clear")}
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <div className="relative">
            <Button variant="outline-primary" size="sm" disabled={isUpdating}>
              {t("common.state")}
            </Button>
            <div className="absolute right-0 top-full z-10 mt-1 w-48 rounded-md border border-border-primary bg-surface-1 py-1 shadow-lg">
              {states.map((state) => (
                <button
                  key={state.id}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-layer-1"
                  onClick={() => handleBulkUpdate({ state_id: state.id })}
                  disabled={isUpdating}
                >
                  <div className="h-2 w-2 rounded-full" style={{ backgroundColor: state.color }} />
                  {state.name}
                </button>
              ))}
            </div>
          </div>

          <div className="relative">
            <Button variant="outline-primary" size="sm" disabled={isUpdating}>
              {t("common.priority")}
            </Button>
            <div className="absolute right-0 top-full z-10 mt-1 w-40 rounded-md border border-border-primary bg-surface-1 py-1 shadow-lg">
              {priorities.map((priority) => (
                <button
                  key={priority.value}
                  className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm hover:bg-layer-1"
                  onClick={() =>
                    handleBulkUpdate({
                      priority: priority.value as "urgent" | "high" | "medium" | "low" | "none",
                    })
                  }
                  disabled={isUpdating}
                >
                  {priority.label}
                </button>
              ))}
            </div>
          </div>

          <Button variant="outline-danger" size="sm" onClick={handleDelete} disabled={isUpdating}>
            {t("common.delete")}
          </Button>
        </div>
      </div>

      {showDeleteModal && user && (
        <BulkDeleteIssuesModal isOpen={showDeleteModal} onClose={() => setShowDeleteModal(false)} user={user} />
      )}
    </>
  );
});
