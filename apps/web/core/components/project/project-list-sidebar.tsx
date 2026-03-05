/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { ArchiveIcon, ClockIcon, StarIcon } from "lucide-react";
// plane imports
import { useTranslation } from "@plane/i18n";
import { cn } from "@plane/utils";
// hooks
import { useProjectFilter } from "@/hooks/store/use-project-filter";

const FILTER_TABS = [
  { key: "all", label: "workspace_projects.filter.all", icon: null },
  { key: "my_projects", label: "workspace_projects.filter.my_projects", icon: null },
  { key: "favorites", label: "workspace_projects.filter.favorites", icon: StarIcon },
  { key: "archived_projects", label: "workspace_projects.filter.archived", icon: ArchiveIcon },
] as const;

export const ProjectListSidebar = observer(function ProjectListSidebar() {
  const { t } = useTranslation();
  const { workspaceSlug } = useParams();
  const { currentWorkspaceAppliedDisplayFilters, currentWorkspaceDisplayFilters, updateDisplayFilters } =
    useProjectFilter();

  const activeFilter = currentWorkspaceAppliedDisplayFilters?.[0] ?? "all";

  const handleFilterChange = (filterKey: string) => {
    if (!workspaceSlug) return;

    const newFilters: Record<string, boolean> = {
      my_projects: filterKey === "my_projects",
      favorites: filterKey === "favorites",
      archived_projects: filterKey === "archived_projects",
    };

    updateDisplayFilters(workspaceSlug.toString(), newFilters);
  };

  return (
    <div className="flex h-full w-56 flex-col border-r border-subtle bg-surface-1">
      <div className="flex flex-col gap-1 p-3">
        {FILTER_TABS.map((filter) => {
          const isActive =
            filter.key === "all"
              ? !currentWorkspaceDisplayFilters?.my_projects &&
                !currentWorkspaceDisplayFilters?.favorites &&
                !currentWorkspaceDisplayFilters?.archived_projects
              : activeFilter === filter.key;

          return (
            <button
              key={filter.key}
              onClick={() => handleFilterChange(filter.key)}
              className={cn(
                "text-sm flex w-full items-center gap-2 rounded-md px-3 py-2 text-left font-medium transition-colors",
                isActive
                  ? "bg-accent-primary/10 text-accent-primary"
                  : "text-secondary hover:bg-layer-2 hover:text-primary"
              )}
            >
              {filter.icon && <filter.icon className="h-4 w-4" />}
              {filter.key === "all" ? t("workspace_projects.filter.all") : t(filter.label)}
            </button>
          );
        })}
      </div>

      <div className="mt-auto border-t border-subtle p-3">
        <button
          className={cn(
            "text-sm flex w-full items-center gap-2 rounded-md px-3 py-2 text-left font-medium text-secondary transition-colors hover:bg-layer-2 hover:text-primary"
          )}
        >
          <ClockIcon className="h-4 w-4" />
          {t("workspace_projects.filter.recent")}
        </button>
      </div>
    </div>
  );
});
