/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useMemo, useState } from "react";
import { BarChart3, Calendar, Download, TrendingUp } from "lucide-react";
import { Button } from "@plane/propel/button";
import type { TWorklog } from "@plane/types";

interface TimeReportsProps {
  worklogs: TWorklog[];
  onExportCSV?: () => void;
}

type ReportPeriod = "daily" | "weekly";

interface DailySummary {
  date: string;
  totalMinutes: number;
  worklogCount: number;
}

const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = minutes % 60;
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
};

export function TimeReports({ worklogs, onExportCSV }: TimeReportsProps) {
  const [period, setPeriod] = useState<ReportPeriod>("daily");

  const summaries = useMemo(() => {
    const grouped: Record<string, DailySummary> = {};

    worklogs.forEach((worklog) => {
      const date = new Date(worklog.started_at);
      let key: string;

      if (period === "daily") {
        key = date.toISOString().split("T")[0];
      } else {
        const dayOfWeek = date.getDay();
        const startOfWeek = new Date(date);
        startOfWeek.setDate(date.getDate() - dayOfWeek);
        key = startOfWeek.toISOString().split("T")[0];
      }

      if (!grouped[key]) {
        grouped[key] = { date: key, totalMinutes: 0, worklogCount: 0 };
      }
      grouped[key].totalMinutes += worklog.duration;
      grouped[key].worklogCount += 1;
    });

    return Object.values(grouped).sort((a, b) => b.date.localeCompare(a.date));
  }, [worklogs, period]);

  const totalMinutes = useMemo(
    () => summaries.reduce((acc, s) => acc + s.totalMinutes, 0),
    [summaries]
  );

  const totalWorklogs = useMemo(
    () => summaries.reduce((acc, s) => acc + s.worklogCount, 0),
    [summaries]
  );

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BarChart3 className="text-text-secondary h-5 w-5" />
          <h3 className="font-semibold">Time Reports</h3>
        </div>
        {onExportCSV && (
          <Button variant="secondary" size="sm" prependIcon={<Download className="h-4 w-4" />} onClick={onExportCSV}>
            Export CSV
          </Button>
        )}
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => setPeriod("daily")}
          className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            period === "daily"
              ? "bg-accent-primary text-white"
              : "bg-surface-2 text-text-secondary hover:bg-surface-3"
          }`}
        >
          <Calendar className="h-4 w-4" />
          Daily
        </button>
        <button
          onClick={() => setPeriod("weekly")}
          className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
            period === "weekly"
              ? "bg-accent-primary text-white"
              : "bg-surface-2 text-text-secondary hover:bg-surface-3"
          }`}
        >
          <TrendingUp className="h-4 w-4" />
          Weekly
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-md bg-surface-2 p-3">
          <p className="text-xs text-text-secondary">Total Time</p>
          <p className="text-xl font-semibold">{formatDuration(totalMinutes)}</p>
        </div>
        <div className="rounded-md bg-surface-2 p-3">
          <p className="text-xs text-text-secondary">Total Entries</p>
          <p className="text-xl font-semibold">{totalWorklogs}</p>
        </div>
      </div>

      {summaries.length > 0 ? (
        <div className="flex flex-col gap-2">
          {summaries.map((summary) => (
            <div
              key={summary.date}
              className="flex items-center justify-between rounded-md border border-subtle bg-surface-2 p-3"
            >
              <div className="flex flex-col">
                <span className="font-medium">{formatDate(summary.date)}</span>
                <span className="text-xs text-text-secondary">{summary.worklogCount} entries</span>
              </div>
              <span className="font-mono font-medium">{formatDuration(summary.totalMinutes)}</span>
            </div>
          ))}
        </div>
      ) : (
        <p className="text-center text-text-secondary">No worklogs recorded yet</p>
      )}
    </div>
  );
}

export function exportWorklogsToCSV(worklogs: TWorklog[]): void {
  const headers = ["Date", "Issue", "Description", "Duration (minutes)", "Started At", "Ended At"];
  const rows = worklogs.map((worklog) => [
    new Date(worklog.started_at).toLocaleDateString(),
    worklog.issue_detail?.name || worklog.issue,
    worklog.description,
    worklog.duration.toString(),
    worklog.started_at,
    worklog.ended_at || "",
  ]);

  const csvContent = [headers, ...rows].map((row) => row.map((cell) => `"${cell}"`).join(",")).join("\n");

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `worklogs_${new Date().toISOString().split("T")[0]}.csv`;
  link.click();
}
