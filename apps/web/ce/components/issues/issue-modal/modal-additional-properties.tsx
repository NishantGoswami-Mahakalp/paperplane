/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { useMemo } from "react";
import { DynamicFormField, isFieldVisible } from "@plane/ui";
import { useWorkItemTypeFields } from "../../../hooks/use-work-item-type-fields";
import type { TWorkItemTypeFieldValue, TWorkItemTypeFieldValues, IWorkItemTypeFieldWithCondition } from "@plane/types";

export type TWorkItemModalAdditionalPropertiesProps = {
  isDraft?: boolean;
  projectId: string | null;
  workItemId: string | undefined;
  workspaceSlug: string;
  onChange?: (values: TWorkItemTypeFieldValues) => void;
  initialValues?: TWorkItemTypeFieldValues;
};

export function WorkItemModalAdditionalProperties(props: TWorkItemModalAdditionalPropertiesProps) {
  const { isDraft, projectId, workItemId, workspaceSlug, onChange, initialValues } = props;

  const {
    schema,
    fieldValues,
    errors,
    isSchemaLoading,
    updateFieldValue,
    validateFields,
    setFieldValues,
  } = useWorkItemTypeFields({
    projectId,
    workspaceSlug,
    workItemTypeId: null,
  });

  React.useEffect(() => {
    if (initialValues) {
      setFieldValues(initialValues);
    }
  }, [initialValues, setFieldValues]);

  React.useEffect(() => {
    if (onChange) {
      onChange(fieldValues);
    }
  }, [fieldValues, onChange]);

  const visibleFields = useMemo(() => {
    if (!schema?.fields) return [];

    return schema.fields.filter((field: IWorkItemTypeFieldWithCondition) => isFieldVisible(field, fieldValues));
  }, [schema?.fields, fieldValues]);

  if (!projectId || isSchemaLoading || !schema) {
    return null;
  }

  if (visibleFields.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="text- font-medium text-secondary">
        Additional Properties
      </div>
      <div className="grid grid-cols-1 gap-4">
        {visibleFields.map((field: IWorkItemTypeFieldWithCondition) => (
          <DynamicFormField
            key={field.id}
            field={field}
            value={fieldValues[field.key]}
            errors={errors}
            onChange={(value: unknown) => updateFieldValue(field.key, value as TWorkItemTypeFieldValue)}
            disabled={isDraft}
            allFieldValues={fieldValues}
          />
        ))}
      </div>
    </div>
  );
}

export { isFieldVisible };
export type { TWorkItemTypeFieldValue, TWorkItemTypeFieldValues };
