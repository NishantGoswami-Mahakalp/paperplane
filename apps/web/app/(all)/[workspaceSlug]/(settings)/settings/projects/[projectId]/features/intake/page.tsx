/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState } from "react";
import { observer } from "mobx-react";
// plane imports
import { useTranslation } from "@plane/i18n";
import { Button, Input } from "@plane/ui";
import type { IIntakeForm, IIntakeFormFieldConfig } from "@plane/types";
// components
import { EUserPermissions, EUserPermissionsLevel } from "@plane/constants";
import { NotAuthorizedView } from "@/components/auth-screens/not-authorized-view";
import { PageHead } from "@/components/core/page-title";
import { SettingsContentWrapper } from "@/components/settings/content-wrapper";
import { SettingsHeading } from "@/components/settings/heading";
import { ProjectSettingsFeatureControlItem } from "@/components/settings/project/content/feature-control-item";
import { IntakeFormBuilder } from "@/components/intake-form-builder";
// hooks
import { useProject } from "@/hooks/store/use-project";
import { useUserPermissions } from "@/hooks/store/user";
// services
import { IntakeFormService } from "@/services/intake-form.service";
import { ProjectPublishService } from "@/services/project";
// local imports
import type { Route } from "./+types/page";
import { FeaturesIntakeProjectSettingsHeader } from "./header";

const intakeFormService = new IntakeFormService();
const projectPublishService = new ProjectPublishService();

function FeaturesIntakeSettingsPage({ params }: Route.ComponentProps) {
  const { workspaceSlug, projectId } = params;
  // store hooks
  const { workspaceUserInfo, allowPermissions } = useUserPermissions();
  const { currentProjectDetails } = useProject();
  // translation
  const { t } = useTranslation();
  // local state
  const [intakeForm, setIntakeForm] = useState<IIntakeForm | null>(null);
  const [fields, setFields] = useState<IIntakeFormFieldConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [publicUrl, setPublicUrl] = useState<string>("");
  const [publishSettings, setPublishSettings] = useState<any>(null);

  // derived values
  const pageTitle = currentProjectDetails?.name
    ? `${currentProjectDetails?.name} settings - ${t("project_settings.features.intake.short_title")}`
    : undefined;
  const canPerformProjectAdminActions = allowPermissions([EUserPermissions.ADMIN], EUserPermissionsLevel.PROJECT);

  useEffect(() => {
    if (!workspaceSlug || !projectId) return;

    const fetchData = async () => {
      setIsLoading(true);
      try {
        const [intakeData, publishData] = await Promise.all([
          intakeFormService.list(workspaceSlug, projectId).catch(() => null),
          projectPublishService.fetchPublishSettings(workspaceSlug, projectId).catch(() => null),
        ]);

        if (intakeData) {
          setIntakeForm(intakeData);
          setFields(intakeData.field_config_json || []);
        }
        if (publishData?.anchor) {
          setPublishSettings(publishData);
          setPublicUrl(`${window.location.origin}/intake/${intakeData?.id || ""}?anchor=${publishData.anchor}`);
        }
      } catch (error) {
        console.error("Failed to fetch intake data:", error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [workspaceSlug, projectId]);

  const handleSave = async () => {
    if (!workspaceSlug || !projectId || !intakeForm?.id) return;

    setIsSaving(true);
    try {
      await intakeFormService.update(workspaceSlug, projectId, intakeForm.id, {
        field_config_json: fields,
      });
      setIntakeForm((prev) => prev ? { ...prev, field_config_json: fields } : null);
    } catch (error) {
      console.error("Failed to save form:", error);
    } finally {
      setIsSaving(false);
    }
  };

  const handlePublish = async () => {
    if (!workspaceSlug || !projectId) return;

    setIsSaving(true);
    try {
      const data = await projectPublishService.publishProject(workspaceSlug, projectId, {
        entity_name: "project",
        entity_identifier: projectId,
      });
      setPublishSettings(data);
      if (data.anchor) {
        setPublicUrl(`${window.location.origin}/intake/${intakeForm?.id || ""}?anchor=${data.anchor}`);
      }
    } catch (error) {
      console.error("Failed to publish form:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (workspaceUserInfo && !canPerformProjectAdminActions) {
    return <NotAuthorizedView section="settings" isProjectView className="h-auto" />;
  }

  if (isLoading) {
    return (
      <SettingsContentWrapper header={<FeaturesIntakeProjectSettingsHeader />}>
        <PageHead title={pageTitle} />
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
        </div>
      </SettingsContentWrapper>
    );
  }

  return (
    <SettingsContentWrapper header={<FeaturesIntakeProjectSettingsHeader />}>
      <PageHead title={pageTitle} />
      <section className="w-full space-y-6">
        <SettingsHeading
          title={t("project_settings.features.intake.title")}
          description={t("project_settings.features.intake.description")}
        />
        <div className="mt-7">
          <ProjectSettingsFeatureControlItem
            title={t("project_settings.features.intake.toggle_title")}
            description={t("project_settings.features.intake.toggle_description")}
            featureProperty="inbox_view"
            projectId={projectId}
            value={!!currentProjectDetails?.inbox_view}
            workspaceSlug={workspaceSlug}
          />
        </div>

        <div className="border-t border-default pt-6">
          <h3 className="text-lg font-semibold mb-4">Public Form Settings</h3>
          
          {publicUrl ? (
            <div className="bg-surface-2 rounded-lg p-4 mb-4">
              <label className="block text-sm font-medium text-secondary mb-2">
                Public Form URL
              </label>
              <div className="flex gap-2">
                <Input value={publicUrl} readOnly className="flex-1" />
                <Button
                  variant="neutral-primary"
                  onClick={() => {
                    navigator.clipboard.writeText(publicUrl);
                  }}
                >
                  Copy
                </Button>
                <Button variant="primary" onClick={() => window.open(publicUrl, "_blank")}>
                  Open
                </Button>
              </div>
              <p className="text-xs text-secondary mt-2">
                Share this URL to let anyone submit entries to your intake
              </p>
            </div>
          ) : (
            <div className="mb-4">
              <p className="text-sm text-secondary mb-3">
                Publish your project to create a public form URL
              </p>
              <Button variant="primary" onClick={handlePublish} disabled={isSaving}>
                {isSaving ? "Publishing..." : "Publish Project"}
              </Button>
            </div>
          )}
        </div>

        <div className="border-t border-default pt-6">
          <h3 className="text-lg font-semibold mb-4">Form Builder</h3>
          <IntakeFormBuilder fields={fields} onChange={setFields} />
          
          <div className="mt-6 flex justify-end">
            <Button variant="primary" onClick={handleSave} disabled={isSaving}>
              {isSaving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>
      </section>
    </SettingsContentWrapper>
  );
}

export default observer(FeaturesIntakeSettingsPage);
