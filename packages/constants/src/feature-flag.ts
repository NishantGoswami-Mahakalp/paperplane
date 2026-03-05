/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { EFeatureFlag, EFeatureFlagLevel, type TFeatureFlag, type TFeatureFlagLevel } from "@plane/types";

export { EFeatureFlag, EFeatureFlagLevel };
export type { TFeatureFlag, TFeatureFlagLevel };

export const FEATURE_FLAGS: Array<{
  key: EFeatureFlag;
  name: string;
  description: string;
  level: TFeatureFlagLevel[];
  defaultEnabled: boolean;
}> = [
  {
    key: EFeatureFlag.AI_ASSISTANT,
    name: "AI Assistant",
    description: "Enable AI-powered assistance features",
    level: [EFeatureFlagLevel.WORKSPACE, EFeatureFlagLevel.USER],
    defaultEnabled: false,
  },
  {
    key: EFeatureFlag.EXPORT,
    name: "Export",
    description: "Enable data export functionality",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.IMPORT,
    name: "Import",
    description: "Enable data import functionality",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.ANALYTICS,
    name: "Analytics",
    description: "Enable workspace analytics",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: false,
  },
  {
    key: EFeatureFlag.GITHUB_IMPORT,
    name: "GitHub Import",
    description: "Enable GitHub import",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.JIRA_IMPORT,
    name: "Jira Import",
    description: "Enable Jira import",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.CUSTOM_ROLES,
    name: "Custom Roles",
    description: "Enable custom role management",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: false,
  },
  {
    key: EFeatureFlag.WEBHOOKS,
    name: "Webhooks",
    description: "Enable webhook configuration",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.API_TOKENS,
    name: "API Tokens",
    description: "Enable API token management",
    level: [EFeatureFlagLevel.WORKSPACE],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.SLA,
    name: "SLA",
    description: "Enable SLA tracking",
    level: [EFeatureFlagLevel.PROJECT],
    defaultEnabled: false,
  },
  {
    key: EFeatureFlag.ISSUE_AUTOMATIONS,
    name: "Issue Automations",
    description: "Enable issue automation rules",
    level: [EFeatureFlagLevel.PROJECT],
    defaultEnabled: true,
  },
  {
    key: EFeatureFlag.WORKFLOW_AUTOMATIONS,
    name: "Workflow Automations",
    description: "Enable workflow automation rules",
    level: [EFeatureFlagLevel.PROJECT],
    defaultEnabled: true,
  },
];

export const WORKSPACE_LEVEL_FEATURE_FLAGS = FEATURE_FLAGS.filter((flag) =>
  flag.level.includes(EFeatureFlagLevel.WORKSPACE)
).map((flag) => flag.key);

export const PROJECT_LEVEL_FEATURE_FLAGS = FEATURE_FLAGS.filter((flag) =>
  flag.level.includes(EFeatureFlagLevel.PROJECT)
).map((flag) => flag.key);

export const USER_LEVEL_FEATURE_FLAGS = FEATURE_FLAGS.filter((flag) =>
  flag.level.includes(EFeatureFlagLevel.USER)
).map((flag) => flag.key);
