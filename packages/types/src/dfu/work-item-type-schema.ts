/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import type { TFieldType, IFieldValidationSchema, ISelectOption, IOptionGroup } from "./field-type-registry";

export interface IWorkItemTypeField {
  id: string;
  name: string;
  key: string;
  type: TFieldType | string;
  description?: string;
  required: boolean;
  validationSchema?: IFieldValidationSchema;
  options?: ISelectOption[];
  optionGroups?: IOptionGroup[];
  defaultValue?: unknown;
  metadata?: Record<string, unknown>;
}

export interface IWorkItemTypeSchema {
  id: string;
  name: string;
  description?: string;
  fields: IWorkItemTypeField[];
}

export interface IConditionalFieldRule {
  field: string;
  operator: "equals" | "not_equals" | "contains" | "not_contains" | "is_empty" | "is_not_empty";
  value?: unknown;
}

export interface IConditionalVisibility {
  condition: "and" | "or";
  rules: IConditionalFieldRule[];
}

export interface IWorkItemTypeFieldWithCondition extends IWorkItemTypeField {
  conditionalVisibility?: IConditionalVisibility;
}

export interface IWorkItemTypeSchemaWithFields extends IWorkItemTypeSchema {
  fields: IWorkItemTypeFieldWithCondition[];
}

export type TWorkItemTypeFieldValue = unknown;

export type TWorkItemTypeFieldValues = Record<string, TWorkItemTypeFieldValue>;

export interface IWorkItemTypeFieldError {
  field: string;
  message: string;
}

export type TWorkItemTypeFieldErrors = Record<string, string>;

export interface IWorkItemTypeFieldConfig {
  field: IWorkItemTypeFieldWithCondition;
  value: TWorkItemTypeFieldValue;
  error?: string;
  onChange: (value: unknown) => void;
  onBlur?: () => void;
  disabled?: boolean;
}
