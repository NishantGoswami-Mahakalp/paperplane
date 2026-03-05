/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { LayoutGrid, List } from "lucide-react";
// plane imports
import { useTranslation } from "@plane/i18n";
import type { TProjectViewType } from "@plane/types";
// hooks
import { useProjectFilter } from "@/hooks/store/use-project-filter";

export const ProjectViewToggle = observer(function ProjectViewToggle() {
  const { t } = useTranslation();
  const { workspaceSlug } = useParams();
  const { currentWorkspaceDisplayFilters, updateDisplayFilters } = useProjectFilter();

  const currentView = currentWorkspaceDisplayFilters?.view_type ?? "grid";

  const handleViewChange = (view: TProjectViewType) => {
    if (!workspaceSlug) return;
    updateDisplayFilters(workspaceSlug.toString(), { view_type: view });
  };

  return (
    <div className="flex items-center gap-1 rounded-md border border-subtle p-0.5">
      <button
        onClick={() => handleViewChange("grid")}
        className={`flex items-center justify-center rounded p-1.5 transition-colors ${
          currentView === "grid"
            ? "text-on-accent-primary bg-accent-primary"
            : "text-secondary hover:bg-layer-2 hover:text-primary"
        }`}
        title={t("workspace_projects.view.grid")}
      >
        <LayoutGrid className="h-4 w-4" />
      </button>
      <button
        onClick={() => handleViewChange("table")}
        className={`flex items-center justify-center rounded p-1.5 transition-colors ${
          currentView === "table"
            ? "text-on-accent-primary bg-accent-primary"
            : "text-secondary hover:bg-layer-2 hover:text-primary"
        }`}
        title={t("workspace_projects.view.table")}
      >
        <List className="h-4 w-4" />
      </button>
    </div>
  );
});
