/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { Outlet } from "react-router";
import { useParams } from "next/navigation";
import { ProjectsAppPowerKProvider } from "@/components/power-k/projects-app-provider";
import { QuickSearchProvider, QuickSearchModal } from "@/components/core/modals/quick-search-modal";
import { useQuickSearchShortcut } from "@/hooks/use-quick-search-shortcut";
// plane web components
import { ProjectAppSidebar } from "./_sidebar";
import { ExtendedProjectSidebar } from "./extended-project-sidebar";

function WorkspaceLayout() {
  const params = useParams();
  const workspaceSlug = params?.workspaceSlug as string;

  useQuickSearchShortcut({ enabled: !!workspaceSlug });

  return (
    <>
      <QuickSearchProvider>
        {workspaceSlug && <QuickSearchModal workspaceSlug={workspaceSlug} />}
        <ProjectsAppPowerKProvider />
        <div className="relative flex h-full w-full flex-col overflow-hidden rounded-lg border border-subtle">
          <div id="full-screen-portal" className="absolute inset-0 w-full" />
          <div className="relative flex size-full overflow-hidden">
            <ProjectAppSidebar />
            <ExtendedProjectSidebar />
            <main className="relative flex h-full w-full flex-col overflow-hidden bg-surface-1">
              <Outlet />
            </main>
          </div>
        </div>
      </QuickSearchProvider>
    </>
  );
}

export default observer(WorkspaceLayout);
