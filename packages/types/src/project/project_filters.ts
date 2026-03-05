/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export type TProjectOrderByOptions =
  | "sort_order"
  | "name"
  | "-name"
  | "created_at"
  | "-created_at"
  | "members_length"
  | "-members_length"
  | "updated_at"
  | "-updated_at";

export type TProjectViewType = "grid" | "table";

export type TProjectDisplayFilters = {
  my_projects?: boolean;
  favorites?: boolean;
  archived_projects?: boolean;
  order_by?: TProjectOrderByOptions;
  view_type?: TProjectViewType;
};

export type TProjectAppliedDisplayFilterKeys = "my_projects" | "favorites" | "archived_projects";

export type TProjectFilters = {
  access?: string[] | null;
  lead?: string[] | null;
  members?: string[] | null;
  created_at?: string[] | null;
};

export type TProjectStoredFilters = {
  display_filters?: TProjectDisplayFilters;
  filters?: TProjectFilters;
};
