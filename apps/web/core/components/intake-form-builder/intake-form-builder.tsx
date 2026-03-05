/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { observer } from "mobx-react";
import { Plus, Trash2, Copy, ArrowUp, ArrowDown } from "lucide-react";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Button, Input, TextArea } from "@plane/ui";
import type { IIntakeFormFieldConfig, IIntakeFormFieldOption, TIntakeFieldType, TIntakeTargetProperty } from "@plane/types";
import { INTAKE_FIELD_TYPE, INTAKE_TARGET_PROPERTY } from "@plane/types";

interface IntakeFormBuilderProps {
  fields: IIntakeFormFieldConfig[];
  onChange: (fields: IIntakeFormFieldConfig[]) => void;
}

const generateId = () => Math.random().toString(36).substring(2, 11);

const FIELD_TYPES: { value: TIntakeFieldType; label: string }[] = [
  { value: INTAKE_FIELD_TYPE.TEXT, label: "Text" },
  { value: INTAKE_FIELD_TYPE.NUMBER, label: "Number" },
  { value: INTAKE_FIELD_TYPE.EMAIL, label: "Email" },
  { value: INTAKE_FIELD_TYPE.URL, label: "URL" },
  { value: INTAKE_FIELD_TYPE.TEXTAREA, label: "Text Area" },
  { value: INTAKE_FIELD_TYPE.SELECT, label: "Select" },
  { value: INTAKE_FIELD_TYPE.MULTI_SELECT, label: "Multi Select" },
  { value: INTAKE_FIELD_TYPE.CHECKBOX, label: "Checkbox" },
  { value: INTAKE_FIELD_TYPE.DATE, label: "Date" },
  { value: INTAKE_FIELD_TYPE.DATE_TIME, label: "Date Time" },
];

const TARGET_PROPERTIES: { value: string; label: string }[] = [
  { value: "", label: "None" },
  { value: INTAKE_TARGET_PROPERTY.NAME, label: "Name" },
  { value: INTAKE_TARGET_PROPERTY.DESCRIPTION, label: "Description" },
  { value: INTAKE_TARGET_PROPERTY.PRIORITY, label: "Priority" },
  { value: INTAKE_TARGET_PROPERTY.STATE, label: "State" },
  { value: INTAKE_TARGET_PROPERTY.ASSIGNEE, label: "Assignee" },
  { value: INTAKE_TARGET_PROPERTY.LABELS, label: "Labels" },
  { value: INTAKE_TARGET_PROPERTY.START_DATE, label: "Start Date" },
  { value: INTAKE_TARGET_PROPERTY.TARGET_DATE, label: "Target Date" },
];

export const IntakeFormBuilder = observer(function IntakeFormBuilder({ fields, onChange }: IntakeFormBuilderProps) {
  const { t } = useTranslation();
  const [expandedField, setExpandedField] = useState<string | null>(null);

  const addField = () => {
    const newField: IIntakeFormFieldConfig = {
      id: generateId(),
      name: `field_${fields.length + 1}`,
      type: INTAKE_FIELD_TYPE.TEXT,
      label: `Field ${fields.length + 1}`,
      placeholder: "",
      description: "",
      required: false,
      options: [],
    };
    onChange([...fields, newField]);
    setExpandedField(newField.id);
  };

  const updateField = (index: number, updates: Partial<IIntakeFormFieldConfig>) => {
    const newFields = [...fields];
    newFields[index] = { ...newFields[index], ...updates };
    onChange(newFields);
  };

  const removeField = (index: number) => {
    const newFields = fields.filter((_, i) => i !== index);
    onChange(newFields);
  };

  const duplicateField = (index: number) => {
    const field = fields[index];
    const newField: IIntakeFormFieldConfig = {
      ...field,
      id: generateId(),
      name: `${field.name}_copy`,
      label: `${field.label} (Copy)`,
    };
    const newFields = [...fields];
    newFields.splice(index + 1, 0, newField);
    onChange(newFields);
  };

  const moveField = (index: number, direction: "up" | "down") => {
    if (
      (direction === "up" && index === 0) ||
      (direction === "down" && index === fields.length - 1)
    ) {
      return;
    }
    const newFields = [...fields];
    const newIndex = direction === "up" ? index - 1 : index + 1;
    [newFields[index], newFields[newIndex]] = [newFields[newIndex], newFields[index]];
    onChange(newFields);
  };

  const addOption = (fieldIndex: number) => {
    const field = fields[fieldIndex];
    if (!field.options) field.options = [];
    const newOption: IIntakeFormFieldOption = {
      id: generateId(),
      label: `Option ${field.options.length + 1}`,
      value: `option_${field.options.length + 1}`,
    };
    const newFields = [...fields];
    newFields[fieldIndex] = {
      ...field,
      options: [...field.options, newOption],
    };
    onChange(newFields);
  };

  const updateOption = (fieldIndex: number, optionIndex: number, updates: Partial<IIntakeFormFieldOption>) => {
    const field = fields[fieldIndex];
    if (!field.options) return;
    const newOptions = [...field.options];
    newOptions[optionIndex] = { ...newOptions[optionIndex], ...updates };
    updateField(fieldIndex, { options: newOptions });
  };

  const removeOption = (fieldIndex: number, optionIndex: number) => {
    const field = fields[fieldIndex];
    if (!field.options) return;
    const newOptions = field.options.filter((_, i) => i !== optionIndex);
    updateField(fieldIndex, { options: newOptions });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Form Fields</h3>
        <Button variant="primary" size="sm" onClick={addField}>
          <Plus className="size-4 mr-1" />
          Add Field
        </Button>
      </div>

      <div className="space-y-3">
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="border border-default rounded-lg bg-background"
          >
            <div
              className="flex items-center gap-3 p-3 cursor-pointer"
              onClick={() => setExpandedField(expandedField === field.id ? null : field.id)}
            >
              <div className="flex flex-col gap-1">
                <button
                  type="button"
                  className="p-1 text-secondary hover:text-primary disabled:opacity-50"
                  disabled={index === 0}
                  onClick={(e) => {
                    e.stopPropagation();
                    moveField(index, "up");
                  }}
                >
                  <ArrowUp className="size-3" />
                </button>
                <button
                  type="button"
                  className="p-1 text-secondary hover:text-primary disabled:opacity-50"
                  disabled={index === fields.length - 1}
                  onClick={(e) => {
                    e.stopPropagation();
                    moveField(index, "down");
                  }}
                >
                  <ArrowDown className="size-3" />
                </button>
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium truncate">{field.label || `Field ${index + 1}`}</span>
                  <span className="text-xs text-secondary px-2 py-0.5 bg-secondary-100 rounded">
                    {field.type}
                  </span>
                  {field.required && (
                    <span className="text-xs text-red-500 px-2 py-0.5 bg-red-50 rounded">
                      Required
                    </span>
                  )}
                </div>
                <p className="text-xs text-secondary truncate">
                  {field.name}
                </p>
              </div>

              <div className="flex items-center gap-1">
                <Button
                  variant="neutral-primary"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    duplicateField(index);
                  }}
                >
                  <Copy className="size-4" />
                </Button>
                <Button
                  variant="neutral-primary"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    removeField(index);
                  }}
                >
                  <Trash2 className="size-4 text-red-500" />
                </Button>
              </div>
            </div>

            {expandedField === field.id && (
              <div className="border-t border-default p-4 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-1">
                      Field Label
                    </label>
                    <Input
                      value={field.label}
                      onChange={(e) => updateField(index, { label: e.target.value })}
                      placeholder="Enter field label"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-1">
                      Field Name (API Key)
                    </label>
                    <Input
                      value={field.name}
                      onChange={(e) => updateField(index, { name: e.target.value })}
                      placeholder="field_name"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-1">
                      Field Type
                    </label>
                    <select
                      className="w-full px-3 py-2 rounded-md border border-default bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      value={field.type}
                      onChange={(e) => updateField(index, { type: e.target.value as TIntakeFieldType })}
                    >
                      {FIELD_TYPES.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary mb-1">
                      Map to Issue Property
                    </label>
                    <select
                      className="w-full px-3 py-2 rounded-md border border-default bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                      value={field.target_property || ""}
                      onChange={(e) => updateField(index, { target_property: e.target.value as TIntakeTargetProperty })}
                    >
                      {TARGET_PROPERTIES.map((prop) => (
                        <option key={prop.value} value={prop.value}>
                          {prop.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary mb-1">
                    Placeholder
                  </label>
                  <Input
                    value={field.placeholder || ""}
                    onChange={(e) => updateField(index, { placeholder: e.target.value })}
                    placeholder="Enter placeholder text"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary mb-1">
                    Description / Help Text
                  </label>
                  <TextArea
                    value={field.description || ""}
                    onChange={(e) => updateField(index, { description: e.target.value })}
                    placeholder="Enter help text for this field"
                    rows={2}
                  />
                </div>

                <div className="flex items-center gap-3">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={field.required}
                      onChange={(e) => updateField(index, { required: e.target.checked })}
                      className="w-4 h-4 rounded border-default text-primary focus:ring-primary"
                    />
                    <span className="text-sm text-secondary">Required field</span>
                  </label>
                </div>

                {(field.type === INTAKE_FIELD_TYPE.SELECT || field.type === INTAKE_FIELD_TYPE.MULTI_SELECT) && (
                  <div className="border border-default rounded p-4 space-y-3">
                    <label className="block text-sm font-medium text-secondary">
                      Options
                    </label>
                    {field.options?.map((option, optIndex) => (
                      <div key={option.id} className="flex items-center gap-2">
                        <Input
                          value={option.label}
                          onChange={(e) => updateOption(index, optIndex, { 
                            label: e.target.value, 
                            value: e.target.value.toLowerCase().replace(/\s+/g, "_") 
                          })}
                          placeholder="Option label"
                          className="flex-1"
                        />
                        <Button
                          variant="neutral-primary"
                          size="sm"
                          onClick={() => removeOption(index, optIndex)}
                        >
                          <Trash2 className="size-4" />
                        </Button>
                      </div>
                    ))}
                    <Button variant="outline-primary" size="sm" onClick={() => addOption(index)}>
                      <Plus className="size-4 mr-1" />
                      Add Option
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {fields.length === 0 && (
        <div className="text-center py-8 border border-dashed border-default rounded-lg">
          <p className="text-secondary mb-2">No fields added yet</p>
          <Button variant="outline-primary" onClick={addField}>
            <Plus className="size-4 mr-1" />
            Add First Field
          </Button>
        </div>
      )}
    </div>
  );
});
