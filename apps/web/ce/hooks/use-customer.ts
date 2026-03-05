/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";

export interface Customer {
  id: string;
  name: string;
  email: string;
  description: string;
  status: "active" | "inactive" | "archived";
  external_source: string | null;
  external_id: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
  issue_count?: number;
  open_issue_count?: number;
  closed_issue_count?: number;
}

export interface CustomerContact {
  id: string;
  name: string;
  email: string | null;
  phone: string | null;
  role: string | null;
  is_primary: boolean;
}

export const useCustomer = () => {
  const [customers] = useState<Customer[]>([]);
  const [isLoading] = useState(false);

  return {
    customers,
    isLoading,
    fetchCustomers: async () => {},
    fetchCustomer: async () => null,
    fetchCustomerIssues: async () => [],
    createCustomer: async () => null,
    updateCustomer: async () => null,
    deleteCustomer: async () => false,
  };
};
