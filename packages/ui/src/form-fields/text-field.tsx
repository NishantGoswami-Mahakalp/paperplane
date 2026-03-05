/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useState, useCallback } from "react";
import { Input } from "./input";
import { TextArea } from "./textarea";
import { ValidationMessage, FormField } from "./root";
import type { IFieldValidationSchema } from "@plane/types";

export interface TextFieldProps {
  id: string;
  name?: string;
  label?: string;
  value?: string;
  placeholder?: string;
  mode?: "single" | "multiline";
  validationSchema?: IFieldValidationSchema;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  inputClassName?: string;
  onChange?: (value: string) => void;
  onBlur?: () => void;
}

export function TextField({
  id,
  name,
  label,
  value = "",
  placeholder,
  mode = "single",
  validationSchema,
  disabled = false,
  readOnly = false,
  className,
  inputClassName,
  onChange,
  onBlur,
}: TextFieldProps) {
  const [error, setError] = useState<string | null>(null);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const newValue = e.target.value;
      onChange?.(newValue);

      if (validationSchema) {
        if (validationSchema.required && (!newValue || newValue.trim() === "")) {
          setError(`${label || "Field"} is required`);
          return;
        }
        if (typeof newValue === "string") {
          if (validationSchema.minLength !== undefined && newValue.length < validationSchema.minLength) {
            setError(`Minimum length is ${validationSchema.minLength} characters`);
            return;
          }
          if (validationSchema.maxLength !== undefined && newValue.length > validationSchema.maxLength) {
            setError(`Maximum length is ${validationSchema.maxLength} characters`);
            return;
          }
        }
      }
      setError(null);
    },
    [onChange, validationSchema, label]
  );

  const handleBlur = useCallback(() => {
    onBlur?.();
  }, [onBlur]);

  const inputProps = {
    id,
    name,
    value,
    placeholder,
    disabled,
    readOnly,
    hasError: !!error,
    onChange: handleChange,
    onBlur: handleBlur,
    className: inputClassName,
  };

  return (
    <FormField label={label || ""} htmlFor={id} className={className}>
      {mode === "multiline" ? <TextArea {...inputProps} /> : <Input {...inputProps} />}
      {error && <ValidationMessage type="error" message={error} />}
    </FormField>
  );
}
