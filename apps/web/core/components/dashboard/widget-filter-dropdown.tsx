/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { observer } from "mobx-react";
import { useTranslation } from "@plane/i18n";
import { CustomSearchSelect } from "@plane/ui";
import { Filter } from "lucide-react";
import type { TWidgetKeys } from "@plane/types";
import { useDashboard } from "@/hooks/store/use-dashboard";

interface WidgetFilterDropdownProps {
  widgetKey: TWidgetKeys;
  widgetId: string;
  workspaceSlug: string;
  dashboardId: string;
  options: { key: string; label: string }[];
  currentFilter: string;
  onFilterChange?: (filter: string) => void;
}

export const WidgetFilterDropdown: React.FC<WidgetFilterDropdownProps> = observer((props) => {
  const { widgetKey, widgetId, workspaceSlug, dashboardId, options, currentFilter, onFilterChange } = props;
  const { t } = useTranslation();
  const { updateDashboardWidgetFilters } = useDashboard();

  const selectOptions = options.map((option) => ({
    value: option.key,
    query: option.label,
    content: (
      <div className="flex max-w-[200px] items-center gap-2">
        <span className="truncate">{option.label}</span>
      </div>
    ),
  }));

  const handleFilterChange = async (value: string) => {
    if (onFilterChange) {
      onFilterChange(value);
      return;
    }

    try {
      await updateDashboardWidgetFilters(workspaceSlug, dashboardId, widgetId, {
        widgetKey,
        filters: {
          duration: value as any,
        },
      });
    } catch (error) {
      console.error("Failed to update widget filter", error);
    }
  };

  const selectedOption = options.find((opt) => opt.key === currentFilter);

  return (
    <CustomSearchSelect
      value={currentFilter ? [currentFilter] : []}
      onChange={(val) => {
        if (val && val.length > 0) {
          handleFilterChange(val[0] as string);
        }
      }}
      options={selectOptions}
      label={
        <div className="text-xs flex items-center gap-1.5 p-1">
          <Filter className="h-3.5 w-3.5" />
          <span className="truncate">{selectedOption?.label || t("dashboard.filters.duration")}</span>
        </div>
      }
      buttonClassName="border border-subtle"
    />
  );
});
