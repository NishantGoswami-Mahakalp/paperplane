/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useCallback, useMemo, useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { ListFilter, Signal, Trash2, User } from "lucide-react";
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
import { useMember } from "@/hooks/store/use-member";
// components
import { Button, CustomMenu } from "@plane/ui";
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
  const {
    getUserDetails,
    project: { getProjectMemberIds, fetchProjectMembers },
  } = useMember();
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

  const handleAssign = useCallback(
    async (assigneeId: string | null) => {
      if (!workspaceSlug || !projectId || selectedIssues.length === 0) return;

      setIsUpdating(true);
      try {
        const payload: TBulkOperationsPayload = {
          issue_ids: selectedIssues,
          properties: {
            assignee_ids: assigneeId ? [assigneeId] : [],
          },
        };
        await issuesStore.issues.bulkUpdateProperties(workspaceSlug, projectId, payload);
        selectionHelpers.handleClearSelection();
      } catch (error) {
        console.error("Error bulk assigning issues:", error);
      } finally {
        setIsUpdating(false);
      }
    },
    [workspaceSlug, projectId, selectedIssues, issuesStore, selectionHelpers]
  );

  if (!isSelectionActive || selectionHelpers.isSelectionDisabled) return null;

  const states = projectState.projectStates || [];
  const priorities = [
    { value: "urgent", label: t("priority.urgent") },
    { value: "high", label: t("priority.high") },
    { value: "medium", label: t("priority.medium") },
    { value: "low", label: t("priority.low") },
    { value: "none", label: t("priority.none") },
  ];

  const projectMemberIds = projectId ? getProjectMemberIds(projectId, false) : null;

  const projectMembers = useMemo(() => {
    if (!projectMemberIds) return [];
    return projectMemberIds.map((id) => getUserDetails(id)).filter((m): m is NonNullable<typeof m> => !!m);
  }, [projectMemberIds, getUserDetails]);

  // Fetch project members when component mounts
  useMemo(() => {
    if (projectId && workspaceSlug && (!projectMemberIds || projectMemberIds.length === 0)) {
      fetchProjectMembers(workspaceSlug, projectId);
    }
  }, [projectId, workspaceSlug, projectMemberIds, fetchProjectMembers]);

  return (
    <>
      <div
        className={cn(
          "border-border-primary shadow-xl fixed bottom-6 left-1/2 z-[50] flex -translate-x-1/2 items-center gap-2 rounded-lg border bg-surface-1 px-4 py-3",
          "max-w-[calc(100vw-3rem)] transition-all duration-200 ease-in-out",
          "max-md:bottom-4 max-md:gap-1.5 max-md:px-3 max-md:py-2",
          className
        )}
      >
        <div className={cn("border-border-primary flex items-center gap-3 border-r", "max-md:gap-2 max-md:pr-2")}>
          <span className={cn("text-sm text-text-secondary font-medium whitespace-nowrap", "max-md:text-xs")}>
            {selectedIssues.length} {selectedIssues.length === 1 ? "item" : "items"} selected
          </span>
          <Button
            variant="link-neutral"
            size="sm"
            onClick={() => selectionHelpers.handleClearSelection()}
            className="text-text-secondary hover:text-text-primary text-xs h-auto p-0"
          >
            {t("common.clear")}
          </Button>
        </div>

        <div className={cn("flex items-center gap-1", "max-md:gap-0.5")}>
          <CustomMenu
            className="relative"
            customButton={
              <Button variant="outline-primary" size="sm" disabled={isUpdating} className="gap-2">
                <ListFilter className="h-3.5 w-3.5" />
                {t("common.state")}
              </Button>
            }
            placement="top-start"
          >
            {states.map((state) => (
              <CustomMenu.MenuItem
                key={state.id}
                onClick={() => handleBulkUpdate({ state_id: state.id })}
                className="flex items-center gap-2"
              >
                <div className="h-2 w-2 flex-shrink-0 rounded-full" style={{ backgroundColor: state.color }} />
                <span className="truncate">{state.name}</span>
              </CustomMenu.MenuItem>
            ))}
          </CustomMenu>

          <CustomMenu
            className="relative"
            customButton={
              <Button variant="outline-primary" size="sm" disabled={isUpdating} className="gap-2">
                <Signal className="h-3.5 w-3.5" />
                {t("common.priority")}
              </Button>
            }
            placement="top-start"
          >
            {priorities.map((priority) => (
              <CustomMenu.MenuItem
                key={priority.value}
                onClick={() =>
                  handleBulkUpdate({
                    priority: priority.value as "urgent" | "high" | "medium" | "low" | "none",
                  })
                }
                className="flex items-center gap-2"
              >
                <span>{priority.label}</span>
              </CustomMenu.MenuItem>
            ))}
          </CustomMenu>

          <CustomMenu
            className="relative"
            customButton={
              <Button variant="outline-primary" size="sm" disabled={isUpdating} className="gap-2">
                <User className="h-3.5 w-3.5" />
                {t("common.assign")}
              </Button>
            }
            placement="top-start"
          >
            <CustomMenu.MenuItem onClick={() => handleAssign(null)} className="flex items-center gap-2">
              <span className="text-text-secondary">{t("common.unassign")}</span>
            </CustomMenu.MenuItem>
            {projectMembers.map((member) => (
              <CustomMenu.MenuItem
                key={member.id}
                onClick={() => handleAssign(member.id || "")}
                className="flex items-center gap-2"
              >
                {member.avatar_url && (
                  <img src={member.avatar_url} alt={member.display_name || ""} className="h-5 w-5 rounded-full" />
                )}
                <span className="truncate">{member.display_name}</span>
              </CustomMenu.MenuItem>
            ))}
          </CustomMenu>

          <Button variant="outline-danger" size="sm" onClick={handleDelete} disabled={isUpdating} className="gap-2">
            <Trash2 className="h-3.5 w-3.5" />
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
