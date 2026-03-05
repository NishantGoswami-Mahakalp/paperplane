/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Breadcrumbs } from "@plane/ui";
// components
import { BreadcrumbLink } from "@/components/common/breadcrumb-link";
// hooks
import { useWorkspace } from "@/hooks/store";

export const CustomersHeader = observer(() => {
  const { t } = useTranslation();
  const { currentWorkspace } = useWorkspace();

  return (
    <div className="relative flex w-full flex-shrink-0 items-center justify-between gap-2 overflow-hidden py-2">
      <Breadcrumbs>
        <Breadcrumbs.Item
          component={
            <BreadcrumbLink
              label={t("workspace")}
              href={`/${currentWorkspace?.slug}/`}
            />
          }
        />
        <Breadcrumbs.Item
          component={
            <BreadcrumbLink
              label={t("customers")}
              href={`/${currentWorkspace?.slug}/customers`}
            />
          }
        />
      </Breadcrumbs>
    </div>
  );
});
