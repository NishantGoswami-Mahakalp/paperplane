/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import Link from "next/link";
import { useParams } from "next/navigation";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Logo } from "@plane/propel/emoji-icon-picker";
import { ArchiveIcon, LinkIcon, LockIcon } from "@plane/propel/icons";
import type { IProject } from "@plane/types";
import { Avatar, AvatarGroup, FavoriteStar } from "@plane/ui";
import { cn, getFileURL, renderFormattedDate } from "@plane/utils";
// components
// hooks
import { useMember } from "@/hooks/store/use-member";
import { useProject } from "@/hooks/store/use-project";
import { CoverImage } from "@/components/common/cover-image";

type ProjectTableRowProps = {
  project: IProject;
};

const ProjectTableRow = observer(function ProjectTableRow({ project }: ProjectTableRowProps) {
  const { workspaceSlug } = useParams();
  const { getUserDetails } = useMember();
  const { addProjectToFavorites, removeProjectFromFavorites } = useProject();

  const isArchived = !!project.archived_at;

  const handleFavoriteToggle = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!workspaceSlug) return;

    if (project.is_favorite) {
      removeProjectFromFavorites(workspaceSlug.toString(), project.id);
    } else {
      addProjectToFavorites(workspaceSlug.toString(), project.id);
    }
  };

  const handleCopyLink = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const link = `${window.location.origin}/${workspaceSlug}/projects/${project.id}/issues`;
    navigator.clipboard.writeText(link);
  };

  return (
    <Link
      href={`/${workspaceSlug}/projects/${project.id}/issues`}
      className={cn(
        "group/table-row flex items-center gap-4 border-b border-subtle px-4 py-3 transition-colors hover:bg-layer-2",
        { "opacity-60": isArchived }
      )}
    >
      <div className="relative h-10 w-10 flex-shrink-0 overflow-hidden rounded">
        <CoverImage
          src={project.cover_image_url}
          alt={project.name}
          className="absolute top-0 left-0 h-full w-full object-cover"
        />
        <div className="absolute inset-0 flex items-center justify-center bg-black/20">
          <Logo logo={project.logo_props} size={16} />
        </div>
      </div>

      <div className="flex min-w-[200px] flex-1 flex-col gap-0.5">
        <div className="flex items-center gap-2">
          <h3 className="truncate font-medium text-primary">{project.name}</h3>
          {isArchived && <ArchiveIcon className="h-3.5 w-3.5 text-placeholder" />}
        </div>
        <div className="flex items-center gap-1">
          <span className="text-11 font-medium text-secondary">{project.identifier}</span>
          {project.network === 0 && <LockIcon className="h-2.5 w-2.5 text-secondary" />}
        </div>
      </div>

      <div className="text-sm flex min-w-[150px] items-center text-secondary">
        {project.description && project.description.trim() !== ""
          ? project.description.substring(0, 50) + (project.description.length > 50 ? "..." : "")
          : `Created ${renderFormattedDate(project.created_at)}`}
      </div>

      <div className="flex min-w-[100px] items-center justify-end">
        {project.members && project.members.length > 0 ? (
          <AvatarGroup showTooltip={false} size="sm">
            {project.members.slice(0, 3).map((memberId) => {
              const member = getUserDetails(memberId);
              if (!member) return null;
              return (
                <Avatar key={member.id} name={member.display_name} src={getFileURL(member.avatar_url)} size="sm" />
              );
            })}
            {project.members.length > 3 && <Avatar name={`+${project.members.length - 3}`} size="sm" />}
          </AvatarGroup>
        ) : (
          <span className="text-11 text-placeholder italic">No members</span>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={handleCopyLink}
          className="flex h-7 w-7 items-center justify-center rounded opacity-0 transition-opacity group-hover/table-row:opacity-100 hover:bg-layer-1"
        >
          <LinkIcon className="h-3.5 w-3.5 text-secondary" />
        </button>
        {!isArchived && (
          <button
            onClick={handleFavoriteToggle}
            className={cn(
              "flex h-7 w-7 items-center justify-center rounded opacity-0 transition-opacity group-hover/table-row:opacity-100 hover:bg-layer-1",
              project.is_favorite && "opacity-100"
            )}
          >
            <FavoriteStar
              buttonClassName="h-7 w-7"
              iconClassName={cn("h-3.5 w-3.5", {
                "text-yellow-500": project.is_favorite,
                "text-secondary": !project.is_favorite,
              })}
              onClick={handleFavoriteToggle}
              selected={!!project.is_favorite}
            />
          </button>
        )}
      </div>
    </Link>
  );
});

type ProjectTableListProps = {
  projectIds: string[];
};

export const ProjectTableList = observer(function ProjectTableList({ projectIds }: ProjectTableListProps) {
  const { t } = useTranslation();
  const { getProjectById } = useProject();

  return (
    <div className="flex flex-col">
      <div className="flex items-center gap-4 border-b border-subtle bg-layer-1 px-4 py-2.5 text-11 font-medium text-secondary">
        <div className="h-10 w-10 flex-shrink-0" />
        <div className="min-w-[200px] flex-1">{t("workspace_projects.table.name")}</div>
        <div className="min-w-[150px]">{t("workspace_projects.table.description")}</div>
        <div className="min-w-[100px] text-right">{t("workspace_projects.table.members")}</div>
        <div className="w-20" />
      </div>

      <div className="flex flex-col">
        {projectIds.map((projectId) => {
          const project = getProjectById(projectId);
          if (!project) return null;
          return <ProjectTableRow key={project.id} project={project} />;
        })}
      </div>
    </div>
  );
});
