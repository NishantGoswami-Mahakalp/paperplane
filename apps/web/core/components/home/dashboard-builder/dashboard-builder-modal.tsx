/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { useTranslation } from "@plane/i18n";
import { EModalWidth, ModalCore } from "@plane/ui";
import { DashboardWidgetsList } from "./widgets-list";

export type TProps = {
  isModalOpen: boolean;
  handleOnClose?: () => void;
};

export const DashboardBuilderModal = observer(function DashboardBuilderModal(props: TProps) {
  const { isModalOpen, handleOnClose } = props;
  const { workspaceSlug } = useParams();
  const { t } = useTranslation();

  if (!workspaceSlug) return null;

  return (
    <ModalCore isOpen={isModalOpen} handleClose={handleOnClose} width={EModalWidth.LG}>
      <div className="p-4">
        <div className="text-xl font-semibold mb-4">{t("dashboard.builder.title")}</div>
        <DashboardWidgetsList workspaceSlug={workspaceSlug.toString()} />
      </div>
    </ModalCore>
  );
});
