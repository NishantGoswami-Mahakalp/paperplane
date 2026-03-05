/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

export const WidgetLoader = () => (
  <div className="flex h-full w-full animate-pulse flex-col gap-3 rounded-md bg-surface-2 p-4">
    <div className="bg-surface-3 h-6 w-32 rounded" />
    <div className="flex flex-1 items-center justify-center">
      <div className="border-surface-3 h-[200px] w-[200px] rounded-full border-4" />
    </div>
    <div className="bg-surface-3 mx-auto h-4 w-24 rounded" />
  </div>
);

export const WidgetCardLoader = () => (
  <div className="flex h-32 w-full animate-pulse flex-col gap-2 rounded-md bg-surface-2 p-4">
    <div className="bg-surface-3 h-4 w-20 rounded" />
    <div className="flex flex-1 items-center gap-3">
      <div className="bg-surface-3 h-10 w-10 rounded" />
      <div className="flex flex-1 flex-col gap-1">
        <div className="bg-surface-3 h-3 w-24 rounded" />
        <div className="bg-surface-3 h-3 w-16 rounded" />
      </div>
    </div>
  </div>
);

export const TrendChartLoader = () => (
  <div className="flex h-full w-full animate-pulse flex-col gap-3 rounded-md bg-surface-2 p-4">
    <div className="flex items-center justify-between">
      <div className="bg-surface-3 h-6 w-32 rounded" />
      <div className="bg-surface-3 h-6 w-24 rounded" />
    </div>
    <div className="flex flex-1 items-end justify-between gap-2 px-4">
      <div className="bg-surface-3 h-[45%] w-full rounded" />
      <div className="bg-surface-3 h-[60%] w-full rounded" />
      <div className="bg-surface-3 h-[35%] w-full rounded" />
      <div className="bg-surface-3 h-[75%] w-full rounded" />
      <div className="bg-surface-3 h-[50%] w-full rounded" />
      <div className="bg-surface-3 h-[80%] w-full rounded" />
      <div className="bg-surface-3 h-[40%] w-full rounded" />
    </div>
    <div className="bg-surface-3 mx-auto h-4 w-24 rounded" />
  </div>
);
