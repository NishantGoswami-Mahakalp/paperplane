/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React from "react";
import { useParams } from "next/navigation";
import useSWR from "swr";
import type { IWorkspaceIntegration } from "@plane/types";
// ui
import { CustomSearchSelect } from "@plane/ui";
// helpers
import { truncateText } from "@plane/utils";
import { ForgejoIntegrationService } from "@/services/integrations/forgejo.service";

type Props = {
  integration: IWorkspaceIntegration;
  value: any;
  label: string | React.ReactNode;
  onChange: (repo: any) => void;
  characterLimit?: number;
};

const forgejoService = new ForgejoIntegrationService();

export function SelectForgejoRepository(props: Props) {
  const { integration, value, label, onChange, characterLimit = 25 } = props;
  const { workspaceSlug } = useParams();

  const fetchForgejoRepos = async () => {
    if (!workspaceSlug) return [];
    return forgejoService.listAllRepositories(workspaceSlug as string, integration.id);
  };

  const { data: userRepositories, isLoading } = useSWR(
    integration && workspaceSlug ? `forgejo-repositories-${integration.id}` : null,
    fetchForgejoRepos,
    { revalidateOnFocus: false }
  );

  const repos = userRepositories?.repositories ?? [];

  const options =
    repos.map((repo: any) => ({
      value: repo.id,
      query: repo.full_name,
      content: <p>{truncateText(repo.full_name, characterLimit)}</p>,
    })) ?? [];

  if (repos.length < 1 && !isLoading) return null;

  return (
    <CustomSearchSelect
      value={value}
      options={options}
      onChange={(val: string) => {
        const selectedRepo = repos.find((r: any) => r.id === val);
        onChange(selectedRepo);
      }}
      label={label}
      optionsClassName="w-48"
    />
  );
}
