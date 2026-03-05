/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useCallback, useMemo, useState } from "react";
import { observer } from "mobx-react";
import { useParams } from "next/navigation";
import { Check, X, Eye, ArrowRightLeft, Calendar, Filter } from "lucide-react";
// plane imports
import { EInboxIssueStatus, EInboxIssueSource } from "@plane/types";
import { cn } from "@plane/utils";
import { Button, Checkbox } from "@plane/ui";
// hooks
import { useProjectInbox } from "@/hooks/store/use-project-inbox";
import { useAppRouter } from "@/hooks/use-app-router";

type TriageColumn = {
  id: string;
  title: string;
  statuses: EInboxIssueStatus[];
  color: string;
};

const TRIAGE_COLUMNS: TriageColumn[] = [
  {
    id: "pending",
    title: "Pending",
    statuses: [EInboxIssueStatus.PENDING],
    color: "bg-yellow-500",
  },
  {
    id: "reviewed",
    title: "Reviewed",
    statuses: [EInboxIssueStatus.SNOOZED, EInboxIssueStatus.DUPLICATE],
    color: "bg-blue-500",
  },
  {
    id: "converted",
    title: "Converted",
    statuses: [EInboxIssueStatus.ACCEPTED],
    color: "bg-green-500",
  },
  {
    id: "rejected",
    title: "Rejected",
    statuses: [EInboxIssueStatus.DECLINED],
    color: "bg-red-500",
  },
];

type TriageBoardProps = {
  workspaceSlug: string;
  projectId: string;
};

export const TriageBoard = observer(function TriageBoard({ workspaceSlug, projectId }: TriageBoardProps) {
  const router = useAppRouter();
  const { inboxIssueId } = useParams();
  
  const {
    inboxIssues,
    inboxIssueIds,
    loader,
    fetchInboxIssues,
    bulkConvertIssues,
    bulkRejectIssues,
  } = useProjectInbox();

  const [selectedIssues, setSelectedIssues] = useState<Set<string>>(new Set());
  const [dateFilter, setDateFilter] = useState<"all" | "today" | "week" | "month">("all");
  const [sourceFilter, setSourceFilter] = useState<EInboxIssueSource | "all">("all");

  const filteredIssuesByColumn = useMemo(() => {
    const result: Record<string, string[]> = {
      pending: [],
      reviewed: [],
      converted: [],
      rejected: [],
    };

    const now = new Date();
    const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());

    inboxIssueIds.forEach((issueId) => {
      const issue = inboxIssues[issueId];
      if (!issue) return;

      // Apply source filter
      if (sourceFilter !== "all" && issue.source !== sourceFilter) {
        return;
      }

      // Apply date filter
      if (dateFilter !== "all") {
        const createdAt = issue.issue?.created_at ? new Date(issue.issue.created_at) : null;
        if (createdAt) {
          if (dateFilter === "today" && createdAt < todayStart) return;
          if (dateFilter === "week") {
            const weekAgo = new Date(todayStart);
            weekAgo.setDate(weekAgo.getDate() - 7);
            if (createdAt < weekAgo) return;
          }
          if (dateFilter === "month") {
            const monthAgo = new Date(todayStart);
            monthAgo.setMonth(monthAgo.getMonth() - 1);
            if (createdAt < monthAgo) return;
          }
        }
      }

      // Assign to columns
      for (const column of TRIAGE_COLUMNS) {
        if (column.statuses.includes(issue.status)) {
          result[column.id].push(issueId);
          break;
        }
      }
    });

    return result;
  }, [inboxIssueIds, inboxIssues, dateFilter, sourceFilter]);

  const handleSelectIssue = useCallback((issueId: string) => {
    setSelectedIssues((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(issueId)) {
        newSet.delete(issueId);
      } else {
        newSet.add(issueId);
      }
      return newSet;
    });
  }, []);

  const handleSelectAllInColumn = useCallback((columnId: string) => {
    const issueIds = filteredIssuesByColumn[columnId];
    const allSelected = issueIds.every((id) => selectedIssues.has(id));
    
    setSelectedIssues((prev) => {
      const newSet = new Set(prev);
      issueIds.forEach((id) => {
        if (allSelected) {
          newSet.delete(id);
        } else {
          newSet.add(id);
        }
      });
      return newSet;
    });
  }, [filteredIssuesByColumn, selectedIssues]);

  const handleConvertSelected = useCallback(async () => {
    if (selectedIssues.size === 0) return;
    
    try {
      await bulkConvertIssues(workspaceSlug, projectId, Array.from(selectedIssues));
      setSelectedIssues(new Set());
      fetchInboxIssues(workspaceSlug, projectId, "mutation-loading");
    } catch (error) {
      console.error("Error converting issues:", error);
    }
  }, [selectedIssues, workspaceSlug, projectId, bulkConvertIssues, fetchInboxIssues]);

  const handleRejectSelected = useCallback(async () => {
    if (selectedIssues.size === 0) return;
    
    try {
      await bulkRejectIssues(workspaceSlug, projectId, Array.from(selectedIssues));
      setSelectedIssues(new Set());
      fetchInboxIssues(workspaceSlug, projectId, "mutation-loading");
    } catch (error) {
      console.error("Error rejecting issues:", error);
    }
  }, [selectedIssues, workspaceSlug, projectId, bulkRejectIssues, fetchInboxIssues]);

  const handleQuickAction = useCallback(async (issueId: string, action: "convert" | "reject" | "preview") => {
    if (action === "preview") {
      router.push(`/${workspaceSlug}/projects/${projectId}/intake?inboxIssueId=${issueId}`);
      return;
    }

    const issue = inboxIssues[issueId];
    if (!issue) return;

    try {
      if (action === "convert") {
        await inboxIssues[issueId].updateInboxIssueStatus(EInboxIssueStatus.ACCEPTED);
      } else if (action === "reject") {
        await inboxIssues[issueId].updateInboxIssueStatus(EInboxIssueStatus.DECLINED);
      }
      fetchInboxIssues(workspaceSlug, projectId, "mutation-loading");
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
    }
  }, [workspaceSlug, projectId, inboxIssues, fetchInboxIssues, router]);

  const getSourceIcon = (source?: EInboxIssueSource) => {
    switch (source) {
      case EInboxIssueSource.EMAIL:
        return "📧";
      case EInboxIssueSource.FORMS:
        return "📝";
      default:
        return "💻";
    }
  };

  if (loader === "init-loading") {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-secondary">Loading...</div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between border-b border-subtle px-4 py-2">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-secondary" />
            <select
              value={dateFilter}
              onChange={(e) => setDateFilter(e.target.value as typeof dateFilter)}
              className="rounded-md border border-subtle bg-surface-2 px-2 py-1 text-sm"
            >
              <option value="all">All time</option>
              <option value="today">Today</option>
              <option value="week">This week</option>
              <option value="month">This month</option>
            </select>
          </div>
          
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-secondary" />
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value as typeof sourceFilter)}
              className="rounded-md border border-subtle bg-surface-2 px-2 py-1 text-sm"
            >
              <option value="all">All sources</option>
              <option value={EInboxIssueSource.EMAIL}>Email</option>
              <option value={EInboxIssueSource.FORMS}>Form</option>
              <option value={EInboxIssueSource.IN_APP}>In App</option>
            </select>
          </div>
        </div>

        {selectedIssues.size > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-secondary">{selectedIssues.size} selected</span>
            <Button
              variant="primary"
              size="sm"
              onClick={handleConvertSelected}
              className="gap-1"
            >
              <Check className="h-4 w-4" />
              Convert
            </Button>
            <Button
              variant="outline-danger"
              size="sm"
              onClick={handleRejectSelected}
              className="gap-1"
            >
              <X className="h-4 w-4" />
              Reject
            </Button>
          </div>
        )}
      </div>

      {/* Board */}
      <div className="flex flex-1 overflow-x-auto">
        {TRIAGE_COLUMNS.map((column) => {
          const columnIssues = filteredIssuesByColumn[column.id];
          const allSelected = columnIssues.length > 0 && columnIssues.every((id) => selectedIssues.has(id));

          return (
            <div
              key={column.id}
              className="flex min-w-[280px] flex-col border-r border-subtle"
            >
              {/* Column Header */}
              <div className="flex items-center justify-between border-b border-subtle bg-surface-2 px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className={cn("h-2 w-2 rounded-full", column.color)} />
                  <span className="font-medium">{column.title}</span>
                  <span className="text-sm text-secondary">({columnIssues.length})</span>
                </div>
                {columnIssues.length > 0 && (
                  <Checkbox
                    checked={allSelected}
                    onChange={() => handleSelectAllInColumn(column.id)}
                  />
                )}
              </div>

              {/* Column Content */}
              <div className="flex-1 overflow-y-auto p-2">
                {columnIssues.length === 0 ? (
                  <div className="flex h-20 items-center justify-center text-sm text-secondary">
                    No items
                  </div>
                ) : (
                  <div className="space-y-2">
                    {columnIssues.map((issueId) => {
                      const issue = inboxIssues[issueId];
                      if (!issue) return null;
                      const isSelected = selectedIssues.has(issueId);
                      const isPending = issue.status === EInboxIssueStatus.PENDING;

                      return (
                        <div
                          key={issueId}
                          className={cn(
                            "group relative rounded-md border border-subtle bg-surface-1 p-3 transition-colors hover:border-primary",
                            isSelected && "border-primary bg-primary/5"
                          )}
                        >
                          <div className="flex items-start gap-2">
                            {isPending && (
                              <Checkbox
                                checked={isSelected}
                                onChange={() => handleSelectIssue(issueId)}
                              />
                            )}
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-1">
                                <span className="text-xs">{getSourceIcon(issue.source)}</span>
                                <span className="truncate text-sm font-medium">
                                  {issue.issue?.name || "Untitled"}
                                </span>
                              </div>
                              {issue.issue?.description_html && (
                                <p className="mt-1 line-clamp-2 text-xs text-secondary">
                                  {issue.issue.description_html.replace(/<[^>]*>/g, "").slice(0, 100)}
                                </p>
                              )}
                              <div className="mt-2 flex items-center gap-2 text-xs text-secondary">
                                <span>
                                  {issue.issue?.created_at
                                    ? new Date(issue.issue.created_at).toLocaleDateString()
                                    : ""}
                                </span>
                              </div>
                            </div>
                          </div>

                          {/* Quick Actions */}
                          {isPending && (
                            <div className="absolute right-2 top-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button
                                onClick={() => handleQuickAction(issueId, "preview")}
                                className="rounded p-1 hover:bg-surface-2"
                                title="Preview"
                              >
                                <Eye className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleQuickAction(issueId, "convert")}
                                className="rounded p-1 hover:bg-green-50 text-green-600"
                                title="Convert"
                              >
                                <ArrowRightLeft className="h-3.5 w-3.5" />
                              </button>
                              <button
                                onClick={() => handleQuickAction(issueId, "reject")}
                                className="rounded p-1 hover:bg-red-50 text-red-600"
                                title="Reject"
                              >
                                <X className="h-3.5 w-3.5" />
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
});
