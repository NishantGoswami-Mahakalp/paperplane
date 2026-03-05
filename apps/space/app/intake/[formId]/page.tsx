/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { redirect } from "react-router";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Button, Input, TextArea } from "@plane/ui";
import type { TIntakeFieldType } from "@plane/types";
import { IntakeFormPublicService, type TIntakeFormConfig, type TIntakeFormSubmissionResponse } from "@plane/services";
// components
import { LogoSpinner } from "@/components/common/logo-spinner";
import type { Route } from "./+types/page";

const intakeFormService = new IntakeFormPublicService();

interface FormField {
  id: string;
  name: string;
  type: TIntakeFieldType;
  label: string;
  placeholder?: string;
  description?: string;
  required: boolean;
  options?: { id: string; label: string; value: string }[];
}

export const clientLoader = async ({ params, request }: Route.ClientLoaderArgs) => {
  const { formId } = params;
  const url = new URL(request.url);
  const anchor = url.searchParams.get("anchor");

  if (!formId) {
    throw redirect("/404");
  }

  if (!anchor) {
    throw redirect("/404");
  }

  try {
    const config = await intakeFormService.getFormConfig(anchor, formId);
    return { config, anchor };
  } catch {
    throw redirect("/404");
  }
};

export default function IntakeFormPage({ loaderData }: Route.ComponentProps) {
  const { t } = useTranslation();
  const { config, anchor } = loaderData as { config: TIntakeFormConfig; anchor: string };
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitResult, setSubmitResult] = useState<TIntakeFormSubmissionResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    const validationErrors: Record<string, string> = {};
    config.fields.forEach((field) => {
      if (field.required && !formData[field.name]) {
        validationErrors[field.name] = `${field.label} is required`;
      }
    });

    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }

    setIsSubmitting(true);
    try {
      const result = await intakeFormService.submitForm(anchor, config.id, {
        fields: formData,
      });
      setSubmitResult(result);
    } catch (error: any) {
      setErrors({ submit: error?.error || "Failed to submit form" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleChange = (fieldName: string, value: string) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }));
    if (errors[fieldName]) {
      setErrors((prev) => ({ ...prev, [fieldName]: "" }));
    }
  };

  if (submitResult?.success) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold mb-2">Thank you!</h1>
          <p className="text-secondary mb-4">{submitResult.message || "Your submission has been received."}</p>
          <Button
            variant="primary"
            onClick={() => {
              setFormData({});
              setSubmitResult(null);
            }}
          >
            Submit Another Response
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-surface-1 border border-default rounded-lg p-6 shadow-sm">
          <h1 className="text-2xl font-bold mb-2">{config.name}</h1>
          {config.description && (
            <p className="text-secondary mb-6">{config.description}</p>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            {config.fields.map((field) => (
              <div key={field.id}>
                <label className="block text-sm font-medium mb-1">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                {renderField(field, formData[field.name] || "", handleChange, errors[field.name])}
                {field.description && (
                  <p className="text-xs text-secondary mt-1">{field.description}</p>
                )}
                {errors[field.name] && (
                  <p className="text-xs text-red-500 mt-1">{errors[field.name]}</p>
                )}
              </div>
            ))}

            {errors.submit && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-red-600 text-sm">
                {errors.submit}
              </div>
            )}

            <Button type="submit" variant="primary" size="lg" disabled={isSubmitting} className="w-full">
              {isSubmitting ? "Submitting..." : "Submit"}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}

function renderField(
  field: FormField,
  value: string,
  onChange: (name: string, value: string) => void,
  error?: string
) {
  switch (field.type) {
    case "textarea":
      return (
        <TextArea
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          placeholder={field.placeholder}
          rows={4}
          className={error ? "border-red-500" : ""}
        />
      );

    case "select":
      return (
        <select
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          className={`w-full px-3 py-2 rounded-md border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary ${
            error ? "border-red-500" : "border-default"
          }`}
        >
          <option value="">{field.placeholder || "Select an option"}</option>
          {field.options?.map((option) => (
            <option key={option.id} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      );

    case "multi_select":
      return (
        <div className="space-y-2">
          {field.options?.map((option) => (
            <label key={option.id} className="flex items-center gap-2">
              <input
                type="checkbox"
                value={option.value}
                checked={(value.split(",").filter(Boolean) || []).includes(option.value)}
                onChange={(e) => {
                  const currentValues = value ? value.split(",").filter(Boolean) : [];
                  if (e.target.checked) {
                    onChange(field.name, [...currentValues, option.value].join(","));
                  } else {
                    onChange(field.name, currentValues.filter((v) => v !== option.value).join(","));
                  }
                }}
                className="w-4 h-4 rounded border-default text-primary focus:ring-primary"
              />
              <span className="text-sm">{option.label}</span>
            </label>
          ))}
        </div>
      );

    case "checkbox":
      return (
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={value === "true"}
            onChange={(e) => onChange(field.name, e.target.checked ? "true" : "false")}
            className="w-4 h-4 rounded border-default text-primary focus:ring-primary"
          />
          <span className="text-sm text-secondary">{field.description || "Enable this option"}</span>
        </label>
      );

    case "number":
      return (
        <Input
          type="number"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          placeholder={field.placeholder}
          className={error ? "border-red-500" : ""}
        />
      );

    case "date":
      return (
        <Input
          type="date"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          className={error ? "border-red-500" : ""}
        />
      );

    case "date_time":
      return (
        <Input
          type="datetime-local"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          className={error ? "border-red-500" : ""}
        />
      );

    case "email":
      return (
        <Input
          type="email"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          placeholder={field.placeholder}
          className={error ? "border-red-500" : ""}
        />
      );

    case "url":
      return (
        <Input
          type="url"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          placeholder={field.placeholder}
          className={error ? "border-red-500" : ""}
        />
      );

    default:
      return (
        <Input
          type="text"
          value={value}
          onChange={(e) => onChange(field.name, e.target.value)}
          placeholder={field.placeholder}
          className={error ? "border-red-500" : ""}
        />
      );
  }
}
