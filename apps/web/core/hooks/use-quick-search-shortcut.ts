/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useCallback } from "react";
import { useQuickSearchContext } from "@/components/core/modals/quick-search-modal";

interface UseQuickSearchShortcutOptions {
  enabled?: boolean;
}

export const useQuickSearchShortcut = ({ enabled = true }: UseQuickSearchShortcutOptions = {}) => {
  const { open } = useQuickSearchContext();

  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (!enabled) return;

      const isMetaOrCtrl = event.metaKey || event.ctrlKey;
      const isK = event.key.toLowerCase() === "k";

      if (isMetaOrCtrl && isK) {
        event.preventDefault();
        open();
      }
    },
    [enabled, open]
  );

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, [handleKeyDown]);
};
