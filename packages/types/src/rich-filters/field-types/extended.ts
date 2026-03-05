/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TFilterValue } from "../expression";
import type { TBaseFilterFieldConfig } from "./shared";

/**
 * Extended filter types
 */
export const EXTENDED_FILTER_FIELD_TYPE = {
  TEXT: "text",
  NUMBER: "number",
} as const;

// -------- TEXT FILTER CONFIGURATIONS --------

type TBaseTextFilterFieldConfig = TBaseFilterFieldConfig & {
  placeholder?: string;
};

/**
 * Text filter configuration - for text-based filtering.
 */
export type TTextFilterFieldConfig<V extends TFilterValue> = TBaseTextFilterFieldConfig & {
  type: typeof EXTENDED_FILTER_FIELD_TYPE.TEXT;
  defaultValue?: V;
};

// -------- NUMBER FILTER CONFIGURATIONS --------

type TBaseNumberFilterFieldConfig = TBaseFilterFieldConfig & {
  min?: number;
  max?: number;
  step?: number;
};

/**
 * Number filter configuration - for numeric filtering.
 */
export type TNumberFilterFieldConfig<V extends TFilterValue> = TBaseNumberFilterFieldConfig & {
  type: typeof EXTENDED_FILTER_FIELD_TYPE.NUMBER;
  defaultValue?: V;
};

// -------- UNION TYPES --------

/**
 * All extended filter configurations
 */
export type TExtendedFilterFieldConfigs<V extends TFilterValue = TFilterValue> =
  | TTextFilterFieldConfig<V>
  | TNumberFilterFieldConfig<V>;
