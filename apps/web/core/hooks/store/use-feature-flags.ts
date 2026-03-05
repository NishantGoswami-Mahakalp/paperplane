/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useCallback, useEffect } from "react";
import { WORKSPACE_LEVEL_FEATURE_FLAGS, PROJECT_LEVEL_FEATURE_FLAGS } from "@plane/constants";
import type { TFeatureFlag } from "@plane/types";
import { useContext } from "react";
import { StoreContext } from "@/lib/store-context";

export const useFeatureFlags = (workspaceSlug: string, projectId?: string) => {
  const store = useContext(StoreContext);

  if (!store) {
    throw new Error("useFeatureFlags must be used within StoreProvider");
  }

  const { featureFlagsStore: featureStore, router } = store;

  const activeWorkspaceSlug = workspaceSlug || router.workspaceSlug;
  const activeProjectId = projectId || router.projectId;

  useEffect(() => {
    if (activeWorkspaceSlug) {
      featureStore.fetchWorkspaceFeatureFlags(activeWorkspaceSlug);
    }
  }, [activeWorkspaceSlug, featureStore]);

  useEffect(() => {
    if (activeWorkspaceSlug && activeProjectId) {
      featureStore.fetchProjectFeatureFlags(activeWorkspaceSlug, activeProjectId);
    }
  }, [activeWorkspaceSlug, activeProjectId, featureStore]);

  const isFeatureEnabled = useCallback(
    (feature: TFeatureFlag): boolean => {
      if (!activeWorkspaceSlug) return false;
      return featureStore.isFeatureEnabled(activeWorkspaceSlug, feature, activeProjectId);
    },
    [activeWorkspaceSlug, activeProjectId, featureStore]
  );

  const isWorkspaceLevelFeature = useCallback((feature: TFeatureFlag): boolean => {
    return WORKSPACE_LEVEL_FEATURE_FLAGS.includes(feature);
  }, []);

  const isProjectLevelFeature = useCallback((feature: TFeatureFlag): boolean => {
    return PROJECT_LEVEL_FEATURE_FLAGS.includes(feature);
  }, []);

  const setFeatureFlag = useCallback(
    async (
      feature: TFeatureFlag,
      enabled: boolean,
      level: "workspace" | "project" | "user",
      entityId?: string
    ) => {
      if (!activeWorkspaceSlug) return;
      const featureLevel = level === "project" ? "PROJECT" : level === "user" ? "USER" : "WORKSPACE";
      await featureStore.setFeatureFlag(activeWorkspaceSlug, feature, enabled, featureLevel, entityId);
    },
    [activeWorkspaceSlug, featureStore]
  );

  const getAllFeatures = useCallback((): Record<TFeatureFlag, boolean> => {
    if (!activeWorkspaceSlug) return {} as Record<TFeatureFlag, boolean>;
    if (activeProjectId) {
      return featureStore.getProjectFeatureFlags(activeWorkspaceSlug, activeProjectId);
    }
    return featureStore.getWorkspaceFeatureFlags(activeWorkspaceSlug);
  }, [activeWorkspaceSlug, activeProjectId, featureStore]);

  return {
    isFeatureEnabled,
    isWorkspaceLevelFeature,
    isProjectLevelFeature,
    setFeatureFlag,
    getAllFeatures,
    isLoading: featureStore.isLoading,
  };
};

export const useFeatureFlag = (
  feature: TFeatureFlag,
  workspaceSlug?: string,
  projectId?: string
): boolean => {
  const { isFeatureEnabled } = useFeatureFlags(workspaceSlug || "", projectId);
  return isFeatureEnabled(feature);
};
