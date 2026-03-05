/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { makeObservable, runInAction, action, observable } from "mobx";
import { computedFn } from "mobx-utils";
import { EFeatureFlag, EFeatureFlagLevel } from "@plane/constants";
import type { EFeatureFlag as TFeatureFlag, TFeatureFlagLevel } from "@plane/types";
import { FEATURE_FLAGS, WORKSPACE_LEVEL_FEATURE_FLAGS, PROJECT_LEVEL_FEATURE_FLAGS } from "@plane/constants";
import type { RootStore } from "@/plane-web/store/root.store";
import { FeatureService, featureService } from "@/services/feature-flag.service";

const workspaceService = new FeatureService();

export interface IFeatureFlagStore {
  workspaceFeatureFlags: Record<string, Record<TFeatureFlag, boolean>>;
  projectFeatureFlags: Record<string, Record<string, Record<TFeatureFlag, boolean>>>;
  userFeatureFlags: Record<string, Record<TFeatureFlag, boolean>>;
  isLoading: boolean;
  fetchedWorkspaces: Set<string>;
  fetchedProjects: Record<string, Set<string>>;

  getWorkspaceFeatureFlags: (workspaceSlug: string) => Record<TFeatureFlag, boolean>;
  getProjectFeatureFlags: (workspaceSlug: string, projectId: string) => Record<TFeatureFlag, boolean>;
  getUserFeatureFlags: (workspaceSlug: string, userId: string) => Record<TFeatureFlag, boolean>;
  isFeatureEnabled: (
    workspaceSlug: string,
    feature: TFeatureFlag,
    projectId?: string
  ) => boolean;
  fetchWorkspaceFeatureFlags: (workspaceSlug: string) => Promise<void>;
  fetchProjectFeatureFlags: (workspaceSlug: string, projectId: string) => Promise<void>;
  setFeatureFlag: (
    workspaceSlug: string,
    feature: TFeatureFlag,
    enabled: boolean,
    level: TFeatureFlagLevel,
    entityId?: string
  ) => Promise<void>;
  clearFeatureFlags: () => void;
}

export class FeatureFlagStore implements IFeatureFlagStore {
  workspaceFeatureFlags: Record<string, Record<TFeatureFlag, boolean>> = {};
  projectFeatureFlags: Record<string, Record<string, Record<TFeatureFlag, boolean>>> = {};
  userFeatureFlags: Record<string, Record<TFeatureFlag, boolean>> = {};
  isLoading = false;
  fetchedWorkspaces = new Set<string>();
  fetchedProjects: Record<string, Set<string>> = {};

  constructor(private store: RootStore) {
    makeObservable(this, {
      workspaceFeatureFlags: observable,
      projectFeatureFlags: observable,
      userFeatureFlags: observable,
      isLoading: observable,
      fetchWorkspaceFeatureFlags: action,
      fetchProjectFeatureFlags: action,
      setFeatureFlag: action,
      clearFeatureFlags: action,
    });
  }

  private getDefaultFeatureFlags = (level: TFeatureFlagLevel): Record<TFeatureFlag, boolean> => {
    const flags = FEATURE_FLAGS.filter((f) => f.level.includes(level));
    return flags.reduce((acc, flag) => {
      acc[flag.key as TFeatureFlag] = flag.defaultEnabled;
      return acc;
    }, {} as Record<TFeatureFlag, boolean>);
  };

  getWorkspaceFeatureFlags = computedFn((workspaceSlug: string): Record<TFeatureFlag, boolean> => {
    if (!this.workspaceFeatureFlags[workspaceSlug]) {
      return this.getDefaultFeatureFlags(EFeatureFlagLevel.WORKSPACE);
    }
    return this.workspaceFeatureFlags[workspaceSlug];
  });

  getProjectFeatureFlags = computedFn(
    (workspaceSlug: string, projectId: string): Record<TFeatureFlag, boolean> => {
      const workspaceFlags = this.getWorkspaceFeatureFlags(workspaceSlug);
      const projectFlags = this.projectFeatureFlags[workspaceSlug]?.[projectId];
      if (!projectFlags) {
        const defaults = this.getDefaultFeatureFlags(EFeatureFlagLevel.PROJECT);
        return { ...workspaceFlags, ...defaults };
      }
      return { ...workspaceFlags, ...projectFlags };
    }
  );

  getUserFeatureFlags = computedFn((workspaceSlug: string, userId: string): Record<TFeatureFlag, boolean> => {
    const workspaceFlags = this.getWorkspaceFeatureFlags(workspaceSlug);
    const userFlags = this.userFeatureFlags[`${workspaceSlug}-${userId}`];
    if (!userFlags) {
      const defaults = this.getDefaultFeatureFlags(EFeatureFlagLevel.USER);
      return { ...workspaceFlags, ...defaults };
    }
    return { ...workspaceFlags, ...userFlags };
  });

  isFeatureEnabled = computedFn(
    (workspaceSlug: string, feature: TFeatureFlag, projectId?: string): boolean => {
      if (PROJECT_LEVEL_FEATURE_FLAGS.includes(feature) && projectId) {
        return this.getProjectFeatureFlags(workspaceSlug, projectId)[feature] ?? false;
      }
      if (WORKSPACE_LEVEL_FEATURE_FLAGS.includes(feature)) {
        return this.getWorkspaceFeatureFlags(workspaceSlug)[feature] ?? false;
      }
      return false;
    }
  );

  fetchWorkspaceFeatureFlags = async (workspaceSlug: string): Promise<void> => {
    if (this.fetchedWorkspaces.has(workspaceSlug)) return;

    try {
      runInAction(() => {
        this.isLoading = true;
      });

      const response = await workspaceService.getFeatureFlags(workspaceSlug);

      runInAction(() => {
        if (response?.values?.workspace?.[workspaceSlug]) {
          this.workspaceFeatureFlags[workspaceSlug] = response.values.workspace[workspaceSlug];
        }
        if (response?.values?.project?.[workspaceSlug]) {
          this.projectFeatureFlags[workspaceSlug] = response.values.project[workspaceSlug];
        }
        this.fetchedWorkspaces.add(workspaceSlug);
        this.isLoading = false;
      });
    } catch (error) {
      console.error("Error fetching workspace feature flags:", error);
      runInAction(() => {
        this.isLoading = false;
      });
    }
  };

  fetchProjectFeatureFlags = async (workspaceSlug: string, projectId: string): Promise<void> => {
    if (!this.fetchedWorkspaces.has(workspaceSlug)) {
      await this.fetchWorkspaceFeatureFlags(workspaceSlug);
    }

    const projectFetched = this.fetchedProjects[workspaceSlug]?.has(projectId);
    if (projectFetched) return;

    try {
      runInAction(() => {
        this.isLoading = true;
      });

      if (!this.fetchedProjects[workspaceSlug]) {
        this.fetchedProjects[workspaceSlug] = new Set();
      }
      this.fetchedProjects[workspaceSlug].add(projectId);

      runInAction(() => {
        this.isLoading = false;
      });
    } catch (error) {
      console.error("Error fetching project feature flags:", error);
      runInAction(() => {
        this.isLoading = false;
      });
    }
  };

  setFeatureFlag = async (
    workspaceSlug: string,
    feature: TFeatureFlag,
    enabled: boolean,
    level: TFeatureFlagLevel,
    entityId?: string
  ): Promise<void> => {
    try {
      await workspaceService.updateFeatureFlag(workspaceSlug, feature, {
        enabled,
        level,
        entity_id: entityId || workspaceSlug,
      });

      runInAction(() => {
        if (level === EFeatureFlagLevel.WORKSPACE) {
          if (!this.workspaceFeatureFlags[workspaceSlug]) {
            this.workspaceFeatureFlags[workspaceSlug] = this.getDefaultFeatureFlags(EFeatureFlagLevel.WORKSPACE);
          }
          this.workspaceFeatureFlags[workspaceSlug][feature] = enabled;
        } else if (level === EFeatureFlagLevel.PROJECT && entityId) {
          if (!this.projectFeatureFlags[workspaceSlug]) {
            this.projectFeatureFlags[workspaceSlug] = {};
          }
          if (!this.projectFeatureFlags[workspaceSlug][entityId]) {
            this.projectFeatureFlags[workspaceSlug][entityId] = this.getDefaultFeatureFlags(EFeatureFlagLevel.PROJECT);
          }
          this.projectFeatureFlags[workspaceSlug][entityId][feature] = enabled;
        } else if (level === EFeatureFlagLevel.USER && entityId) {
          const key = `${workspaceSlug}-${entityId}`;
          if (!this.userFeatureFlags[key]) {
            this.userFeatureFlags[key] = this.getDefaultFeatureFlags(EFeatureFlagLevel.USER);
          }
          this.userFeatureFlags[key][feature] = enabled;
        }
      });
    } catch (error) {
      console.error("Error setting feature flag:", error);
      throw error;
    }
  };

  clearFeatureFlags = (): void => {
    this.workspaceFeatureFlags = {};
    this.projectFeatureFlags = {};
    this.userFeatureFlags = {};
    this.fetchedWorkspaces.clear();
    this.fetchedProjects = {};
  };
}
