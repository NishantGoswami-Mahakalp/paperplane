/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TExtendedSupportedOperators } from "@plane/types";
import { EXTENDED_EQUALITY_OPERATOR, EXTENDED_COLLECTION_OPERATOR, EXTENDED_COMPARISON_OPERATOR } from "@plane/types";

/**
 * Extended operator labels
 */
export const EXTENDED_OPERATOR_LABELS_MAP: Record<TExtendedSupportedOperators, string> = {
  [EXTENDED_EQUALITY_OPERATOR.EQUALS]: "is",
  [EXTENDED_EQUALITY_OPERATOR.NOT_EQUALS]: "is not",
  [EXTENDED_EQUALITY_OPERATOR.CONTAINS]: "contains",
  [EXTENDED_EQUALITY_OPERATOR.STARTS_WITH]: "starts with",
  [EXTENDED_EQUALITY_OPERATOR.GREATER_THAN]: "greater than",
  [EXTENDED_EQUALITY_OPERATOR.LESS_THAN]: "less than",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ANY]: "contains any",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ALL]: "contains all",
  [EXTENDED_COMPARISON_OPERATOR.BEFORE]: "before",
  [EXTENDED_COMPARISON_OPERATOR.AFTER]: "after",
} as const;

/**
 * Extended date-specific operator labels
 */
export const EXTENDED_DATE_OPERATOR_LABELS_MAP: Record<TExtendedSupportedOperators, string> = {
  [EXTENDED_EQUALITY_OPERATOR.EQUALS]: "is",
  [EXTENDED_EQUALITY_OPERATOR.NOT_EQUALS]: "is not",
  [EXTENDED_COMPARISON_OPERATOR.BEFORE]: "before",
  [EXTENDED_COMPARISON_OPERATOR.AFTER]: "after",
  [EXTENDED_EQUALITY_OPERATOR.CONTAINS]: "contains",
  [EXTENDED_EQUALITY_OPERATOR.STARTS_WITH]: "starts with",
  [EXTENDED_EQUALITY_OPERATOR.GREATER_THAN]: "greater than",
  [EXTENDED_EQUALITY_OPERATOR.LESS_THAN]: "less than",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ANY]: "contains any",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ALL]: "contains all",
} as const;

/**
 * Negated operator labels for all operators
 */
export const NEGATED_OPERATOR_LABELS_MAP: Record<TExtendedSupportedOperators, string> = {
  [EXTENDED_EQUALITY_OPERATOR.EQUALS]: "is not",
  [EXTENDED_EQUALITY_OPERATOR.NOT_EQUALS]: "is",
  [EXTENDED_EQUALITY_OPERATOR.CONTAINS]: "does not contain",
  [EXTENDED_EQUALITY_OPERATOR.STARTS_WITH]: "does not start with",
  [EXTENDED_EQUALITY_OPERATOR.GREATER_THAN]: "less than or equal",
  [EXTENDED_EQUALITY_OPERATOR.LESS_THAN]: "greater than or equal",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ANY]: "does not contain any",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ALL]: "does not contain all",
  [EXTENDED_COMPARISON_OPERATOR.BEFORE]: "after",
  [EXTENDED_COMPARISON_OPERATOR.AFTER]: "before",
} as const;

/**
 * Negated date operator labels for all date operators
 */
export const NEGATED_DATE_OPERATOR_LABELS_MAP: Record<TExtendedSupportedOperators, string> = {
  [EXTENDED_EQUALITY_OPERATOR.EQUALS]: "is not",
  [EXTENDED_EQUALITY_OPERATOR.NOT_EQUALS]: "is",
  [EXTENDED_COMPARISON_OPERATOR.BEFORE]: "after",
  [EXTENDED_COMPARISON_OPERATOR.AFTER]: "before",
  [EXTENDED_EQUALITY_OPERATOR.CONTAINS]: "does not contain",
  [EXTENDED_EQUALITY_OPERATOR.STARTS_WITH]: "does not start with",
  [EXTENDED_EQUALITY_OPERATOR.GREATER_THAN]: "less than or equal",
  [EXTENDED_EQUALITY_OPERATOR.LESS_THAN]: "greater than or equal",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ANY]: "does not contain any",
  [EXTENDED_COLLECTION_OPERATOR.CONTAINS_ALL]: "does not contain all",
} as const;
