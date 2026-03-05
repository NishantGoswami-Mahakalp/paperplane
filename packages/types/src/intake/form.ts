/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export const INTAKE_FIELD_TYPE = {
  TEXT: "text",
  NUMBER: "number",
  EMAIL: "email",
  URL: "url",
  TEXTAREA: "textarea",
  SELECT: "select",
  MULTI_SELECT: "multi_select",
  CHECKBOX: "checkbox",
  DATE: "date",
  DATE_TIME: "date_time",
} as const;

export type TIntakeFieldType = (typeof INTAKE_FIELD_TYPE)[keyof typeof INTAKE_FIELD_TYPE];

export const INTAKE_TARGET_PROPERTY = {
  NAME: "name",
  DESCRIPTION: "description",
  PRIORITY: "priority",
  STATE: "state",
  ASSIGNEE: "assignee",
  LABELS: "labels",
  START_DATE: "start_date",
  TARGET_DATE: "target_date",
} as const;

export type TIntakeTargetProperty = (typeof INTAKE_TARGET_PROPERTY)[keyof typeof INTAKE_TARGET_PROPERTY];

export type TIntakeTargetType = (typeof INTAKE_TARGET_PROPERTY)[keyof typeof INTAKE_TARGET_PROPERTY];

export interface IIntakeFormFieldOption {
  id: string;
  label: string;
  value: string;
}

export interface IIntakeFormFieldConfig {
  id: string;
  name: string;
  type: TIntakeFieldType;
  label: string;
  placeholder?: string;
  description?: string;
  required: boolean;
  options?: IIntakeFormFieldOption[];
  defaultValue?: string | number | boolean | string[];
  min?: number;
  max?: number;
  pattern?: string;
  minLength?: number;
  maxLength?: number;
  target_property?: TIntakeTargetProperty;
}

export interface IIntakeForm {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  is_active: boolean;
  field_config_json: IIntakeFormFieldConfig[];
  created_at: string;
  updated_at: string;
}

export interface IIntakeFieldMapping {
  id: string;
  form_id: string;
  field_name: string;
  target_property: TIntakeTargetProperty;
  target_type: TIntakeFieldType;
  is_required: boolean;
  default_value?: string | number | boolean | string[];
  transformation?: string;
}

export const INTAKE_FIELD_TYPE_COMPATIBILITY: Record<TIntakeFieldType, TIntakeTargetProperty[]> = {
  [INTAKE_FIELD_TYPE.TEXT]: [
    INTAKE_TARGET_PROPERTY.NAME,
    INTAKE_TARGET_PROPERTY.DESCRIPTION,
    INTAKE_TARGET_PROPERTY.PRIORITY,
    INTAKE_TARGET_PROPERTY.STATE,
    INTAKE_TARGET_PROPERTY.ASSIGNEE,
    INTAKE_TARGET_PROPERTY.LABELS,
    INTAKE_TARGET_PROPERTY.START_DATE,
    INTAKE_TARGET_PROPERTY.TARGET_DATE,
  ],
  [INTAKE_FIELD_TYPE.NUMBER]: [
    INTAKE_TARGET_PROPERTY.PRIORITY,
    INTAKE_TARGET_PROPERTY.STATE,
    INTAKE_TARGET_PROPERTY.START_DATE,
    INTAKE_TARGET_PROPERTY.TARGET_DATE,
  ],
  [INTAKE_FIELD_TYPE.EMAIL]: [
    INTAKE_TARGET_PROPERTY.NAME,
    INTAKE_TARGET_PROPERTY.DESCRIPTION,
    INTAKE_TARGET_PROPERTY.ASSIGNEE,
  ],
  [INTAKE_FIELD_TYPE.URL]: [INTAKE_TARGET_PROPERTY.NAME, INTAKE_TARGET_PROPERTY.DESCRIPTION],
  [INTAKE_FIELD_TYPE.TEXTAREA]: [INTAKE_TARGET_PROPERTY.NAME, INTAKE_TARGET_PROPERTY.DESCRIPTION],
  [INTAKE_FIELD_TYPE.SELECT]: [
    INTAKE_TARGET_PROPERTY.PRIORITY,
    INTAKE_TARGET_PROPERTY.STATE,
    INTAKE_TARGET_PROPERTY.ASSIGNEE,
    INTAKE_TARGET_PROPERTY.LABELS,
    INTAKE_TARGET_PROPERTY.START_DATE,
    INTAKE_TARGET_PROPERTY.TARGET_DATE,
  ],
  [INTAKE_FIELD_TYPE.MULTI_SELECT]: [INTAKE_TARGET_PROPERTY.LABELS],
  [INTAKE_FIELD_TYPE.CHECKBOX]: [INTAKE_TARGET_PROPERTY.PRIORITY, INTAKE_TARGET_PROPERTY.STATE],
  [INTAKE_FIELD_TYPE.DATE]: [INTAKE_TARGET_PROPERTY.START_DATE, INTAKE_TARGET_PROPERTY.TARGET_DATE],
  [INTAKE_FIELD_TYPE.DATE_TIME]: [INTAKE_TARGET_PROPERTY.START_DATE, INTAKE_TARGET_PROPERTY.TARGET_DATE],
};

export function isFieldTypeCompatibleWithTarget(
  fieldType: TIntakeFieldType,
  targetProperty: TIntakeTargetProperty
): boolean {
  const compatibleTargets = INTAKE_FIELD_TYPE_COMPATIBILITY[fieldType];
  return compatibleTargets?.includes(targetProperty) ?? false;
}

export function validateFieldMapping(
  fieldType: TIntakeFieldType,
  targetProperty: TIntakeTargetProperty,
  isRequired: boolean
): { valid: boolean; error?: string } {
  if (!isFieldTypeCompatibleWithTarget(fieldType, targetProperty)) {
    return {
      valid: false,
      error: `Cannot map ${fieldType} field to ${targetProperty} property. Incompatible field type.`,
    };
  }

  if (
    isRequired &&
    targetProperty === INTAKE_TARGET_PROPERTY.NAME &&
    fieldType !== INTAKE_FIELD_TYPE.TEXT &&
    fieldType !== INTAKE_FIELD_TYPE.TEXTAREA
  ) {
    return {
      valid: false,
      error: `Name property requires text or textarea field type, got ${fieldType}.`,
    };
  }

  return { valid: true };
}
