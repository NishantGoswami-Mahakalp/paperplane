/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState, useCallback, useEffect, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  type IWorkItemTypeSchemaWithFields,
  type IWorkItemTypeFieldWithCondition,
  type TWorkItemTypeFieldValue,
  type TWorkItemTypeFieldErrors,
  type TWorkItemTypeFieldValues,
} from "@plane/types";

export interface UseWorkItemTypeFieldsProps {
  projectId: string | null;
  workspaceSlug: string;
  workItemTypeId?: string | null;
}

export interface UseWorkItemTypeFieldsReturn {
  schema: IWorkItemTypeSchemaWithFields | null;
  fieldValues: TWorkItemTypeFieldValues;
  errors: TWorkItemTypeFieldErrors;
  isLoading: boolean;
  isSchemaLoading: boolean;
  updateFieldValue: (fieldKey: string, value: TWorkItemTypeFieldValue) => void;
  validateFields: () => boolean;
  resetFieldValues: () => void;
  setFieldValues: (values: TWorkItemTypeFieldValues) => void;
}

const MOCK_SCHEMA: IWorkItemTypeSchemaWithFields = {
  id: "task",
  name: "Task",
  description: "Standard task work item type",
  fields: [
    {
      id: "priority-field",
      name: "Priority",
      key: "priority",
      type: "select",
      required: true,
      options: [
        { value: "none", label: "None" },
        { value: "urgent", label: "Urgent" },
        { value: "high", label: "High" },
        { value: "medium", label: "Medium" },
        { value: "low", label: "Low" },
      ],
      validationSchema: {
        required: true,
      },
    },
    {
      id: "tags-field",
      name: "Tags",
      key: "tags",
      type: "multi_select",
      required: false,
      options: [
        { value: "bug", label: "Bug" },
        { value: "feature", label: "Feature" },
        { value: "enhancement", label: "Enhancement" },
        { value: "documentation", label: "Documentation" },
      ],
    },
    {
      id: "estimated-hours",
      name: "Estimated Hours",
      key: "estimated_hours",
      type: "number",
      required: false,
      validationSchema: {
        min: 0,
        max: 1000,
      },
    },
    {
      id: "start-date-field",
      name: "Start Date",
      key: "start_date",
      type: "date",
      required: false,
    },
    {
      id: "due-date-field",
      name: "Due Date",
      key: "due_date",
      type: "date",
      required: false,
    },
    {
      id: "description-field",
      name: "Description",
      key: "description",
      type: "text_multiline",
      required: false,
      validationSchema: {
        maxLength: 5000,
      },
    },
    {
      id: "external-link",
      name: "External Link",
      key: "external_link",
      type: "url",
      required: false,
    },
    {
      id: "contact-email",
      name: "Contact Email",
      key: "contact_email",
      type: "email",
      required: false,
    },
    {
      id: "status-note",
      name: "Status Note",
      key: "status_note",
      type: "text",
      required: false,
      conditionalVisibility: {
        condition: "and",
        rules: [
          {
            field: "priority",
            operator: "equals",
            value: "urgent",
          },
        ],
      },
    },
  ],
};

export function useWorkItemTypeFields(
  props: UseWorkItemTypeFieldsProps
): UseWorkItemTypeFieldsReturn {
  const { projectId, workspaceSlug, workItemTypeId } = props;
  const [schema, setSchema] = useState<IWorkItemTypeSchemaWithFields | null>(null);
  const [fieldValues, setFieldValues] = useState<TWorkItemTypeFieldValues>({});
  const [errors, setErrors] = useState<TWorkItemTypeFieldErrors>({});
  const [isSchemaLoading, setIsSchemaLoading] = useState(false);

  useEffect(() => {
    if (!projectId || !workItemTypeId) {
      setSchema(null);
      return;
    }

    setIsSchemaLoading(true);

    setTimeout(() => {
      setSchema(MOCK_SCHEMA);
      const initialValues: TWorkItemTypeFieldValues = {};
      MOCK_SCHEMA.fields.forEach((field) => {
        initialValues[field.key] = field.defaultValue ?? (field.type === "multi_select" ? [] : "");
      });
      setFieldValues(initialValues);
      setIsSchemaLoading(false);
    }, 100);
  }, [projectId, workItemTypeId]);

  const updateFieldValue = useCallback((fieldKey: string, value: TWorkItemTypeFieldValue) => {
    setFieldValues((prev) => ({
      ...prev,
      [fieldKey]: value,
    }));

    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[fieldKey];
      return newErrors;
    });
  }, []);

  const validateFields = useCallback(() => {
    if (!schema) return true;

    const newErrors: TWorkItemTypeFieldErrors = {};
    let isValid = true;

    schema.fields.forEach((field) => {
      const value = fieldValues[field.key];
      const isVisible = true;

      if (!isVisible) return;

      if (field.required) {
        if (
          value === undefined ||
          value === null ||
          (typeof value === "string" && value.trim() === "") ||
          (Array.isArray(value) && value.length === 0)
        ) {
          newErrors[field.key] = `${field.name} is required`;
          isValid = false;
        }
      }
    });

    setErrors(newErrors);
    return isValid;
  }, [schema, fieldValues]);

  const resetFieldValues = useCallback(() => {
    if (!schema) return;

    const initialValues: TWorkItemTypeFieldValues = {};
    schema.fields.forEach((field) => {
      initialValues[field.key] = field.defaultValue ?? (field.type === "multi_select" ? [] : "");
    });
    setFieldValues(initialValues);
    setErrors({});
  }, [schema]);

  const setFieldValuesAndValidate = useCallback((values: TWorkItemTypeFieldValues) => {
    setFieldValues(values);
    setErrors({});
  }, []);

  return {
    schema,
    fieldValues,
    errors,
    isLoading: false,
    isSchemaLoading,
    updateFieldValue,
    validateFields,
    resetFieldValues,
    setFieldValues: setFieldValuesAndValidate,
  };
}
