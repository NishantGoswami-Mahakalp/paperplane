/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useState, useCallback } from "react";
import { Calendar } from "@plane/propel/calendar";
import type { Matcher } from "@plane/propel/calendar";
import { CalendarDays } from "lucide-react";
import { FormField, ValidationMessage } from "./root";
import type { IFieldValidationSchema } from "@plane/types";

const formatDate = (date: Date | null | undefined): string => {
  if (!date) return "";
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
};

export interface DateFieldProps {
  id: string;
  name?: string;
  label?: string;
  value?: Date | null;
  placeholder?: string;
  validationSchema?: IFieldValidationSchema;
  minDate?: Date;
  maxDate?: Date;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  onChange?: (value: Date | null) => void;
  onBlur?: () => void;
}

export function DateField({
  id,
  name,
  label,
  value,
  placeholder = "Select date",
  validationSchema,
  minDate,
  maxDate,
  disabled = false,
  readOnly = false,
  className,
  onChange,
  onBlur,
}: DateFieldProps) {
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  const handleDateSelect = useCallback(
    (date: Date | undefined) => {
      const selectedDate = date ?? null;

      if (selectedDate && validationSchema) {
        if (validationSchema.allowFuture === false && selectedDate > new Date()) {
          setError("Future dates are not allowed");
          return;
        }
        if (validationSchema.allowPast === false && selectedDate < new Date()) {
          setError("Past dates are not allowed");
          return;
        }
      }

      setError(null);
      onChange?.(selectedDate);
    },
    [onChange, validationSchema]
  );

  const handleBlur = useCallback(() => {
    onBlur?.();
  }, [onBlur]);

  const disabledDays: Matcher[] = [];
  if (minDate) disabledDays.push({ before: minDate });
  if (maxDate) disabledDays.push({ after: maxDate });

  return (
    <FormField label={label || ""} htmlFor={id} className={className}>
      <div className="relative">
        <button
          type="button"
          id={id}
          name={name}
          disabled={disabled || readOnly}
          onClick={() => !disabled && !readOnly && setIsOpen(!isOpen)}
          onBlur={handleBlur}
          className={`flex w-full items-center gap-2 rounded-md border border-subtle-1 bg-layer-2 px-3 py-2 text-left text-13 focus:ring-1 focus:ring-accent-strong focus:outline-none ${disabled || readOnly ? "cursor-not-allowed opacity-50" : "cursor-pointer"} ${error ? "border-danger-strong" : ""} `}
        >
          <CalendarDays className="h-4 w-4 flex-shrink-0 text-secondary" />
          <span className={value ? "text-primary" : "text-placeholder"}>{value ? formatDate(value) : placeholder}</span>
        </button>

        {isOpen && !disabled && !readOnly && (
          <div className="absolute z-50 mt-1 rounded-md border border-subtle-1 bg-surface-1 shadow-raised-200">
            <Calendar
              mode="single"
              selected={value ?? undefined}
              onSelect={handleDateSelect}
              disabled={disabledDays}
              showOutsideDays
              fixedWeeks
            />
          </div>
        )}
      </div>
      {error && <ValidationMessage type="error" message={error} />}
    </FormField>
  );
}
