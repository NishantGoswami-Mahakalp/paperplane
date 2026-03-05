/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useState, useCallback } from "react";
import { Input } from "./input";
import { ValidationMessage, FormField } from "./root";
import type { IFieldValidationSchema } from "@plane/types";

export interface NumberFieldProps {
  id: string;
  name?: string;
  label?: string;
  value?: number;
  placeholder?: string;
  mode?: "number" | "integer" | "float";
  validationSchema?: IFieldValidationSchema;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  inputClassName?: string;
  onChange?: (value: number | undefined) => void;
  onBlur?: () => void;
}

export function NumberField({
  id,
  name,
  label,
  value,
  placeholder,
  mode = "number",
  validationSchema,
  disabled = false,
  readOnly = false,
  className,
  inputClassName,
  onChange,
  onBlur,
}: NumberFieldProps) {
  const [error, setError] = useState<string | null>(null);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const inputValue = e.target.value;

      if (inputValue === "") {
        onChange?.(undefined);
        setError(null);
        return;
      }

      const numValue = parseFloat(inputValue);

      if (isNaN(numValue)) {
        return;
      }

      if (mode === "integer" && !Number.isInteger(numValue)) {
        setError("Please enter a whole number");
        return;
      }

      if (validationSchema) {
        if (validationSchema.min !== undefined && numValue < validationSchema.min) {
          setError(`Minimum value is ${validationSchema.min}`);
          return;
        }
        if (validationSchema.max !== undefined && numValue > validationSchema.max) {
          setError(`Maximum value is ${validationSchema.max}`);
          return;
        }
        if (mode === "integer" && validationSchema.integer && !Number.isInteger(numValue)) {
          setError("Value must be an integer");
          return;
        }
        if (mode === "float" && validationSchema.float) {
          const decimalPlaces = (numValue.toString().split(".")[1] || "").length;
          if (validationSchema.step !== undefined) {
            const stepDecimalPlaces = (validationSchema.step.toString().split(".")[1] || "").length;
            if (decimalPlaces > stepDecimalPlaces) {
              setError(`Maximum ${stepDecimalPlaces} decimal places allowed`);
              return;
            }
          }
        }
      }

      setError(null);
      onChange?.(numValue);
    },
    [onChange, validationSchema, mode]
  );

  const handleBlur = useCallback(() => {
    onBlur?.();
  }, [onBlur]);

  const getInputType = () => {
    if (mode === "integer") return "number";
    return "number";
  };

  const getStep = () => {
    if (mode === "integer") return "1";
    if (mode === "float" && validationSchema?.step) return validationSchema.step.toString();
    return "any";
  };

  return (
    <FormField label={label || ""} htmlFor={id} className={className}>
      <Input
        id={id}
        name={name}
        type={getInputType()}
        value={value ?? ""}
        placeholder={placeholder}
        step={getStep()}
        disabled={disabled}
        readOnly={readOnly}
        hasError={!!error}
        onChange={handleChange}
        onBlur={handleBlur}
        className={inputClassName}
      />
      {error && <ValidationMessage type="error" message={error} />}
    </FormField>
  );
}
