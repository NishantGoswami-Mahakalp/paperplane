/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { Button, Input } from "@plane/ui";

export const CustomerListRoot = () => {
  return (
    <div className="h-full w-full p-4">
      <div className="mb-4 flex items-center justify-between">
        <h1 className="text-2xl font-semibold">Customers</h1>
        <Button>Add Customer</Button>
      </div>

      <div className="mb-4">
        <Input placeholder="Search customers..." />
      </div>

      <div className="text-gray-500 flex h-64 items-center justify-center">Customer list will appear here</div>
    </div>
  );
};
