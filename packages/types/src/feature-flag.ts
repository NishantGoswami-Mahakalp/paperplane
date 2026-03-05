/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export enum EFeatureFlag {
  AI_ASSISTANT = "ai_assistant",
  EXPORT = "export",
  IMPORT = "import",
  ANALYTICS = "analytics",
  GITHUB_IMPORT = "github_import",
  JIRA_IMPORT = "jira_import",
  CUSTOM_ROLES = "custom_roles",
  WEBHOOKS = "webhooks",
  API_TOKENS = "api_tokens",
  SLA = "sla",
  ISSUE_AUTOMATIONS = "issue_automations",
  WORKFLOW_AUTOMATIONS = "workflow_automations",
}

export type TFeatureFlag = EFeatureFlag;

export enum EFeatureFlagLevel {
  WORKSPACE = "WORKSPACE",
  PROJECT = "PROJECT",
  USER = "USER",
}

export type TFeatureFlagLevel = EFeatureFlagLevel;

export interface IFeatureFlag {
  id: string;
  key: EFeatureFlag;
  name: string;
  description: string;
  level: TFeatureFlagLevel;
}

export interface IFeatureFlagValue {
  workspace: Record<string, boolean>;
  project: Record<string, Record<string, boolean>>;
  user: Record<string, Record<string, boolean>>;
}

export interface IFeatureFlagsResponse {
  flags: IFeatureFlag[];
  values: IFeatureFlagValue;
}

export interface IWorkspaceFeatureFlags {
  [workspaceSlug: string]: Record<EFeatureFlag, boolean>;
}

export interface IProjectFeatureFlags {
  [workspaceSlug: string]: {
    [projectId: string]: Record<EFeatureFlag, boolean>;
  };
}

export interface IUserFeatureFlags {
  [workspaceSlug: string]: {
    [userId: string]: Record<EFeatureFlag, boolean>;
  };
}

export interface IFeatureFlagInput {
  feature_flag: EFeatureFlag;
  level: TFeatureFlagLevel;
  entity_id: string;
  enabled: boolean;
}
