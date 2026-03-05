/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useState, useCallback, useMemo, useEffect } from "react";
import { Dropdown } from "../dropdown";
import { ValidationMessage, FormField } from "./root";
import { cn } from "../utils";
import type { IFieldValidationSchema, ISelectOption, IOptionGroup } from "@plane/types";
import type { TDropdownOption } from "../dropdown/dropdown";

export interface SelectFieldProps {
  id: string;
  name?: string;
  label?: string;
  value?: string;
  placeholder?: string;
  options?: ISelectOption[];
  optionGroups?: IOptionGroup[];
  dynamicOptionsUrl?: string;
  dynamicOptionsFetcher?: () => Promise<ISelectOption[]>;
  validationSchema?: IFieldValidationSchema;
  disabled?: boolean;
  readOnly?: boolean;
  className?: string;
  buttonClassName?: string;
  optionsContainerClassName?: string;
  disableSearch?: boolean;
  onChange?: (value: string) => void;
  onBlur?: () => void;
}

export function SelectField({
  id,
  name: _name,
  label,
  value = "",
  placeholder = "Select an option",
  options: staticOptions,
  optionGroups: _optionGroups,
  dynamicOptionsUrl: _dynamicOptionsUrl,
  dynamicOptionsFetcher,
  validationSchema,
  disabled = false,
  readOnly = false,
  className,
  buttonClassName,
  optionsContainerClassName,
  disableSearch = false,
  onChange,
  onBlur,
}: SelectFieldProps) {
  const [error, setError] = useState<string | null>(null);
  const [options, setOptions] = useState<ISelectOption[]>(staticOptions || []);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (dynamicOptionsFetcher) {
      setLoading(true);
      dynamicOptionsFetcher()
        .then((fetchedOptions) => {
          setOptions(fetchedOptions);
          return fetchedOptions;
        })
        .catch(() => {
          setOptions([]);
          return [];
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [dynamicOptionsFetcher]);

  const dropdownOptions: TDropdownOption[] = useMemo(() => {
    return options.map((option) => ({
      data: option,
      value: option.value,
      disabled: option.disabled,
    }));
  }, [options]);

  const selectedOption = useMemo(() => {
    return options.find((option) => option.value === value);
  }, [options, value]);

  const handleChange = useCallback(
    (newValue: string) => {
      onChange?.(newValue);

      if (validationSchema) {
        if (validationSchema.required && (!newValue || newValue === "")) {
          setError(`${label || "Field"} is required`);
          return;
        }
      }
      setError(null);
    },
    [onChange, validationSchema, label]
  );

  const _handleBlur = useCallback(() => {
    onBlur?.();
  }, [onBlur]);

  const renderButtonContent = useCallback(
    (_isOpen: boolean) => {
      if (loading) {
        return <span className="text-text-secondary">Loading...</span>;
      }
      return (
        <span className={cn(!selectedOption && "text-text-secondary")}>{selectedOption?.label || placeholder}</span>
      );
    },
    [selectedOption, placeholder, loading]
  );

  const renderItem = useCallback(
    ({ value: optionValue, selected }: { value: string; selected: boolean }) => {
      const option = options.find((o) => o.value === optionValue);
      return (
        <div className="flex items-center justify-between">
          <span>{option?.label}</span>
          {selected && <span className="text-xs">✓</span>}
        </div>
      );
    },
    [options]
  );

  return (
    <FormField label={label || ""} htmlFor={id} className={className}>
      <Dropdown
        value={value}
        onChange={handleChange}
        options={dropdownOptions}
        buttonContent={renderButtonContent}
        buttonClassName={buttonClassName}
        optionsContainerClassName={optionsContainerClassName}
        disableSearch={disableSearch}
        inputPlaceholder="Search..."
        disabled={disabled || readOnly || loading}
        keyExtractor={(option) => option.value}
        renderItem={renderItem}
        loader={loading}
      />
      {error && <ValidationMessage type="error" message={error} />}
    </FormField>
  );
}
