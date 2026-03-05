/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { observer } from "mobx-react";
import { useSearchParams } from "next/navigation";
import { useTheme } from "next-themes";
import { LayoutGrid, List } from "lucide-react";
// plane imports
import { EUserPermissionsLevel } from "@plane/constants";
import { useTranslation } from "@plane/i18n";
import { EUserProjectRoles, EInboxIssueCurrentTab } from "@plane/types";
import { Button } from "@plane/ui";
// assets
import darkIntakeAsset from "@/app/assets/empty-state/disabled-feature/intake-dark.webp?url";
import lightIntakeAsset from "@/app/assets/empty-state/disabled-feature/intake-light.webp?url";
// components
import { PageHead } from "@/components/core/page-title";
import { DetailedEmptyState } from "@/components/empty-state/detailed-empty-state-root";
import { InboxIssueRoot } from "@/components/inbox";
import { TriageBoard } from "@/components/inbox/triage-board";
// hooks
import { useProject } from "@/hooks/store/use-project";
import { useUserPermissions } from "@/hooks/store/user";
import { useAppRouter } from "@/hooks/use-app-router";
import type { Route } from "./+types/page";

type ViewMode = "list" | "board";

function ProjectInboxPage({ params }: Route.ComponentProps) {
  /// router
  const router = useAppRouter();
  const { workspaceSlug, projectId } = params;
  const searchParams = useSearchParams();
  const navigationTab = searchParams.get("currentTab");
  const inboxIssueId = searchParams.get("inboxIssueId");
  // theme hook
  const { resolvedTheme } = useTheme();
  // plane hooks
  const { t } = useTranslation();
  // hooks
  const { currentProjectDetails } = useProject();
  const { allowPermissions } = useUserPermissions();
  // view mode state
  const [viewMode, setViewMode] = useState<ViewMode>("list");

  // derived values
  const canPerformEmptyStateActions = allowPermissions([EUserProjectRoles.ADMIN], EUserPermissionsLevel.PROJECT);
  const resolvedPath = resolvedTheme === "light" ? lightIntakeAsset : darkIntakeAsset;

  // No access to inbox
  if (currentProjectDetails?.inbox_view === false)
    return (
      <div className="flex h-full w-full items-center justify-center">
        <DetailedEmptyState
          title={t("disabled_project.empty_state.inbox.title")}
          description={t("disabled_project.empty_state.inbox.description")}
          assetPath={resolvedPath}
          primaryButton={{
            text: t("disabled_project.empty_state.inbox.primary_button.text"),
            onClick: () => {
              router.push(`/${workspaceSlug}/settings/projects/${projectId}/features`);
            },
            disabled: !canPerformEmptyStateActions,
          }}
        />
      </div>
    );

  // derived values
  const pageTitle = currentProjectDetails?.name
    ? t("inbox_issue.page_label", {
        workspace: currentProjectDetails?.name,
      })
    : t("inbox_issue.page_label", {
        workspace: "Plane",
      });

  const currentNavigationTab = navigationTab
    ? navigationTab === "open"
      ? EInboxIssueCurrentTab.OPEN
      : EInboxIssueCurrentTab.CLOSED
    : undefined;

  return (
    <div className="flex h-full flex-col">
      <PageHead title={pageTitle} />
      {/* View Toggle */}
      <div className="flex items-center justify-between border-b border-subtle px-4 py-2">
        <div className="flex items-center gap-2">
          <Button
            variant={viewMode === "list" ? "primary" : "neutral-primary"}
            size="sm"
            onClick={() => setViewMode("list")}
            className="gap-1"
          >
            <List className="h-4 w-4" />
            List
          </Button>
          <Button
            variant={viewMode === "board" ? "primary" : "neutral-primary"}
            size="sm"
            onClick={() => setViewMode("board")}
            className="gap-1"
          >
            <LayoutGrid className="h-4 w-4" />
            Triage
          </Button>
        </div>
      </div>
      <div className="h-full w-full overflow-hidden">
        {viewMode === "board" ? (
          <TriageBoard
            workspaceSlug={workspaceSlug}
            projectId={projectId}
          />
        ) : (
          <InboxIssueRoot
            workspaceSlug={workspaceSlug}
            projectId={projectId}
            inboxIssueId={inboxIssueId || undefined}
            inboxAccessible={currentProjectDetails?.inbox_view || false}
            navigationTab={currentNavigationTab}
          />
        )}
      </div>
    </div>
  );
}

export default observer(ProjectInboxPage);
