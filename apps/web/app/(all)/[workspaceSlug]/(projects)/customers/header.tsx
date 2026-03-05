/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useTranslation } from "react-i18next";
import { observer } from "mobx-react";
// components
import { Breadcrumbs } from "@/components/breadcrumbs";
// hooks
import { useWorkspace } from "@/hooks/store";

export const CustomersHeader = observer(() => {
  const { t } = useTranslation();
  const { currentWorkspace } = useWorkspace();

  const breadcrumbs = [
    {
      title: t("workspace"),
      href: `/${currentWorkspace?.slug}/`,
    },
    {
      title: t("customers"),
      href: `/${currentWorkspace?.slug}/customers`,
    },
  ];

  return (
    <div className="relative flex w-full flex-shrink-0 items-center justify-between gap-2 overflow-hidden py-2">
      <Breadcrumbs breadcrumbs={breadcrumbs} />
    </div>
  );
});
