/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { EUserPermissions, EUserPermissionsLevel } from "@plane/constants";
import { Button } from "@plane/propel/button";
import { Tooltip } from "@plane/propel/tooltip";
import type { IAppIntegration } from "@plane/types";
// assets
import GithubLogo from "@/app/assets/services/github.png?url";
import SlackLogo from "@/app/assets/services/slack.png?url";
import GiteaLogo from "@/app/assets/logos/gitea-logo.svg?url";
// hooks
import { useInstance } from "@/hooks/store/use-instance";
import { useUserPermissions } from "@/hooks/store/user";
import useIntegrationPopup from "@/hooks/use-integration-popup";
import { usePlatformOS } from "@/hooks/use-platform-os";

type Props = {
  integration: IAppIntegration;
};

const integrationDetails: { [key: string]: any } = {
  github: {
    logo: GithubLogo,
    notInstalled: "Connect with GitHub with your Plane workspace to sync project work items.",
  },
  slack: {
    logo: SlackLogo,
    notInstalled: "Connect with Slack with your Plane workspace to sync project work items.",
  },
  forgejo: {
    logo: GiteaLogo,
    notInstalled: "Forgejo project sync is available after workspace setup is wired into this screen.",
  },
};

export const SingleIntegrationCard = observer(function SingleIntegrationCard({ integration }: Props) {
  // router
  const { workspaceSlug } = useParams();
  // store hooks
  const { config } = useInstance();
  const { allowPermissions } = useUserPermissions();

  const isUserAdmin = allowPermissions([EUserPermissions.ADMIN], EUserPermissionsLevel.WORKSPACE);
  const isWorkspaceConnectable = integration.provider !== "forgejo";
  const { isMobile } = usePlatformOS();
  const { startAuth, isConnecting: isInstalling } = useIntegrationPopup({
    provider: integration.provider,
    github_app_name: config?.github_app_name || "",
    slack_client_id: config?.slack_client_id || "",
  });

  return (
    <div className="flex items-center justify-between gap-2 border-b border-subtle bg-surface-1 px-4 py-6">
      <div className="flex items-start gap-4">
        <div className="h-10 w-10 flex-shrink-0">
          <img
            src={integrationDetails[integration.provider].logo}
            className="h-full w-full object-cover"
            alt={`${integration.title} Logo`}
          />
        </div>
        <div>
          <h3 className="flex items-center gap-2 text-body-xs-medium">{integration.title}</h3>
          <p className="text-body-xs-regular text-secondary">{integrationDetails[integration.provider].notInstalled}</p>
        </div>
      </div>

      <Tooltip
        isMobile={isMobile}
        disabled={isUserAdmin && isWorkspaceConnectable}
        tooltipContent={
          !isUserAdmin
            ? "You don't have permission to perform this"
            : !isWorkspaceConnectable
              ? "Forgejo install is not wired into the workspace settings page yet."
              : null
        }
      >
        <Button
          className={`${!isUserAdmin || !isWorkspaceConnectable ? "hover:cursor-not-allowed" : ""}`}
          variant="primary"
          onClick={() => {
            if (!isUserAdmin || !isWorkspaceConnectable || !workspaceSlug) return;
            startAuth();
          }}
          disabled={!isUserAdmin || !isWorkspaceConnectable}
          loading={isInstalling}
        >
          {isInstalling ? "Connecting..." : isWorkspaceConnectable ? "Connect" : "Coming soon"}
        </Button>
      </Tooltip>
    </div>
  );
});
