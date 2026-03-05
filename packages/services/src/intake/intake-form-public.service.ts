/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { API_BASE_URL } from "@plane/constants";
import type { IIntakeFormFieldConfig } from "@plane/types";
import { APIService } from "../api.service";

export interface TIntakeFormConfig {
  id: string;
  name: string;
  description?: string;
  fields: IIntakeFormFieldConfig[];
}

export interface TIntakeFormSubmission {
  fields: Record<string, string | number | boolean | string[]>;
  captcha_token?: string;
}

export interface TIntakeFormSubmissionResponse {
  success: boolean;
  message: string;
  issue: any;
}

export class IntakeFormPublicService extends APIService {
  constructor(BASE_URL?: string) {
    super(BASE_URL || API_BASE_URL);
  }

  async getFormConfig(anchor: string, formId: string): Promise<TIntakeFormConfig> {
    return this.get(`/api/anchor/${anchor}/intake/${formId}/config/`)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }

  async submitForm(anchor: string, formId: string, data: TIntakeFormSubmission): Promise<TIntakeFormSubmissionResponse> {
    return this.post(`/api/anchor/${anchor}/intake/${formId}/submit/`, data)
      .then((response) => response?.data)
      .catch((error) => {
        throw error?.response?.data;
      });
  }
}
