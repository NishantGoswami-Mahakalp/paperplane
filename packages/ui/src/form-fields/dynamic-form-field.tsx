/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { Input } from "./input";
import { TextArea } from "./textarea";
import { NumberField } from "./number-field";
import { SelectField } from "./select-field";
import { MultiSelectField } from "./multi-select-field";
import { DateField } from "./date-field";
import { DateTimeField } from "./date-time-field";
import { ValidationMessage, FormField } from "./root";
import { fieldTypeRegistry, FIELD_TYPE } from "@plane/types";
import type {
  IWorkItemTypeFieldWithCondition,
  TWorkItemTypeFieldValue,
  TWorkItemTypeFieldErrors,
} from "@plane/types";

export interface DynamicFormFieldProps {
  field: IWorkItemTypeFieldWithCondition;
  value: TWorkItemTypeFieldValue;
  errors?: TWorkItemTypeFieldErrors;
  onChange: (value: unknown) => void;
  onBlur?: () => void;
  disabled?: boolean;
  allFieldValues?: Record<string, TWorkItemTypeFieldValue>;
}

export function DynamicFormField({
  field,
  value,
  errors,
  onChange,
  onBlur,
  disabled = false,
  allFieldValues = {},
}: DynamicFormFieldProps) {
  const [error, setError] = useState<string | undefined>(undefined);

  const fieldTypeMetadata = useMemo(() => {
    return fieldTypeRegistry.getType(field.type);
  }, [field.type]);

  const validationSchema = useMemo(() => {
    return field.validationSchema || fieldTypeMetadata?.validationSchema;
  }, [field.validationSchema, fieldTypeMetadata]);

  useEffect(() => {
    if (errors && errors[field.key]) {
      setError(errors[field.key]);
    } else {
      setError(undefined);
    }
  }, [errors, field.key]);

  const validateOnChange = useCallback(
    (newValue: unknown) => {
      if (!validationSchema) return true;

      const validationResult = fieldTypeRegistry.validateValue(field.type, newValue);

      if (!validationResult.valid) {
        setError(validationResult.error);
        return false;
      }

      if (validationSchema.required && (newValue === undefined || newValue === null || newValue === "")) {
        const errorMsg = `${field.name} is required`;
        setError(errorMsg);
        return false;
      }

      setError(undefined);
      return true;
    },
    [field.type, field.name, validationSchema, fieldTypeRegistry]
  );

  const handleChange = useCallback(
    (newValue: unknown) => {
      const isValid = validateOnChange(newValue);
      if (isValid) {
        onChange(newValue);
      }
    },
    [onChange, validateOnChange]
  );

  const handleBlur = useCallback(() => {
    if (validationSchema) {
      const validationResult = fieldTypeRegistry.validateValue(field.type, value);
      if (!validationResult.valid) {
        setError(validationResult.error);
      } else if (validationSchema.required && (value === undefined || value === null || value === "")) {
        setError(`${field.name} is required`);
      } else {
        setError(undefined);
      }
    }
    onBlur?.();
  }, [field.type, field.name, value, validationSchema, fieldTypeRegistry, onBlur]);

  const renderField = useCallback(() => {
    const fieldType = field.type as unknown;
    const isDisabled = disabled || field.metadata?.disabled === true;

    switch (fieldType) {
      case FIELD_TYPE.TEXT:
        return (
          <Input
            id={field.key}
            name={field.key}
            value={(value as string) ?? ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder={fieldTypeMetadata?.name || "Enter text"}
            maxLength={validationSchema?.maxLength}
          />
        );

      case FIELD_TYPE.TEXT_MULTILINE:
        return (
          <TextArea
            id={field.key}
            name={field.key}
            value={(value as string) ?? ""}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder={fieldTypeMetadata?.name || "Enter text"}
            rows={3}
          />
        );

      case FIELD_TYPE.NUMBER:
      case FIELD_TYPE.NUMBER_INTEGER:
      case FIELD_TYPE.NUMBER_FLOAT:
        return (
          <NumberField
            id={field.key}
            name={field.key}
            value={(value as number) ?? 0}
            onChange={(val?: number) => handleChange(val ?? 0)}
            onBlur={handleBlur}
            disabled={isDisabled}
            mode={
              fieldType === FIELD_TYPE.NUMBER_INTEGER
                ? "integer"
                : fieldType === FIELD_TYPE.NUMBER_FLOAT
                  ? "float"
                  : "number"
            }
            validationSchema={validationSchema}
          />
        );

      case FIELD_TYPE.EMAIL:
        return (
          <Input
            id={field.key}
            name={field.key}
            type="email"
            value={(value as string) ?? ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder="Enter email"
          />
        );

      case FIELD_TYPE.URL:
        return (
          <Input
            id={field.key}
            name={field.key}
            type="url"
            value={(value as string) ?? ""}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder="Enter URL"
          />
        );

      case FIELD_TYPE.DATE: {
        const dateValue = value
          ? value instanceof Date
            ? value
            : typeof value === "string"
              ? new Date(value)
              : null
          : null;
        return (
          <DateField
            id={field.key}
            name={field.key}
            value={dateValue}
            onChange={(val: Date | null) => handleChange(val ? val.toISOString().split("T")[0] : null)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder="Select date"
            validationSchema={validationSchema}
          />
        );
      }

      case FIELD_TYPE.DATE_TIME: {
        const dateTimeValue = value
          ? value instanceof Date
            ? value
            : typeof value === "string"
              ? new Date(value)
              : null
          : null;
        return (
          <DateTimeField
            id={field.key}
            name={field.key}
            value={dateTimeValue}
            onChange={(val: Date | null) => handleChange(val ? val.toISOString() : null)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder="Select date and time"
            validationSchema={validationSchema}
          />
        );
      }

      case FIELD_TYPE.SELECT:
        return (
          <SelectField
            id={field.key}
            name={field.key}
            value={(value as string) ?? ""}
            onChange={(val) => handleChange(val)}
            onBlur={handleBlur}
            disabled={isDisabled}
            options={field.options || fieldTypeMetadata?.options || []}
            optionGroups={field.optionGroups || fieldTypeMetadata?.optionGroups}
            placeholder="Select an option"
            label={field.name}
          />
        );

      case FIELD_TYPE.MULTI_SELECT:
        return (
          <MultiSelectField
            id={field.key}
            name={field.key}
            value={(value as string[]) ?? []}
            onChange={(val) => handleChange(val)}
            onBlur={handleBlur}
            disabled={isDisabled}
            options={field.options || fieldTypeMetadata?.options || []}
            optionGroups={field.optionGroups || fieldTypeMetadata?.optionGroups}
            placeholder="Select options"
            label={field.name}
            validationSchema={validationSchema}
          />
        );

      default:
        return (
          <Input
            id={field.key}
            name={field.key}
            value={String(value ?? "")}
            onChange={(e) => handleChange(e.target.value)}
            onBlur={handleBlur}
            disabled={isDisabled}
            placeholder={`Enter ${field.name}`}
          />
        );
    }
  }, [
    field,
    value,
    handleChange,
    handleBlur,
    disabled,
    fieldTypeMetadata,
    validationSchema,
  ]);

  const shouldRenderSelectWrappers = field.type !== FIELD_TYPE.SELECT && field.type !== FIELD_TYPE.MULTI_SELECT;

  if (shouldRenderSelectWrappers) {
    return (
      <FormField label={field.name} htmlFor={field.key} optional={!field.required}>
        {renderField()}
        {error && <ValidationMessage type="error" message={error} />}
      </FormField>
    );
  }

  return (
    <>
      {renderField()}
      {error && <ValidationMessage type="error" message={error} />}
    </>
  );
}

export function isFieldVisible(
  field: IWorkItemTypeFieldWithCondition,
  allFieldValues: Record<string, TWorkItemTypeFieldValue>
): boolean {
  const conditionalVisibility = field.conditionalVisibility;

  if (!conditionalVisibility || !conditionalVisibility.rules || conditionalVisibility.rules.length === 0) {
    return true;
  }

  const evaluateRule = (rule: (typeof conditionalVisibility.rules)[number]): boolean => {
    const fieldValue = allFieldValues[rule.field];

    switch (rule.operator) {
      case "equals":
        return fieldValue === rule.value;
      case "not_equals":
        return fieldValue !== rule.value;
      case "contains":
        if (typeof fieldValue === "string" && typeof rule.value === "string") {
          return fieldValue.includes(rule.value);
        }
        return false;
      case "not_contains":
        if (typeof fieldValue === "string" && typeof rule.value === "string") {
          return !fieldValue.includes(rule.value);
        }
        return true;
      case "is_empty":
        return fieldValue === undefined || fieldValue === null || fieldValue === "";
      case "is_not_empty":
        return fieldValue !== undefined && fieldValue !== null && fieldValue !== "";
      default:
        return true;
    }
  };

  if (conditionalVisibility.condition === "and") {
    return conditionalVisibility.rules.every(evaluateRule);
  }

  return conditionalVisibility.rules.some(evaluateRule);
}
