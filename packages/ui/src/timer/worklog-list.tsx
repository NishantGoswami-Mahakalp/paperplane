/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { Clock, Pencil, Trash2, MoreHorizontal } from "lucide-react";
import { Avatar } from "../avatar/avatar";
import { Button } from "../button/button";

interface WorkLog {
  id: string;
  description: string;
  duration: number;
  started_at: string;
  ended_at: string | null;
  actor_detail: {
    id: string;
    first_name: string;
    last_name: string;
    avatar_url: string;
    display_name: string;
  };
  created_at: string;
}

interface WorkLogListProps {
  worklogs: WorkLog[];
  currentUserId?: string;
  onEdit?: (worklogId: string) => void;
  onDelete?: (worklogId: string) => void;
  onStartTimer?: (worklogId?: string) => void;
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  if (minutes > 0) {
    return `${minutes}m ${secs}s`;
  }
  return `${secs}s`;
};

const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  const yesterday = new Date(now);
  yesterday.setDate(yesterday.getDate() - 1);
  const isYesterday = date.toDateString() === yesterday.toDateString();

  if (isToday) {
    return `Today at ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  }
  if (isYesterday) {
    return `Yesterday at ${date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}`;
  }
  return date.toLocaleDateString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

export function WorkLogList({ worklogs, currentUserId, onEdit, onDelete, onStartTimer }: WorkLogListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (worklogs.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <Clock className="text-text-secondary mb-2 h-8 w-8" />
        <p className="text-sm text-text-secondary">No worklogs yet</p>
        <Button variant="outline-primary" size="sm" className="mt-2" onClick={() => onStartTimer?.()}>
          Start Timer
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-2">
      {worklogs.map((worklog) => {
        const isOwn = currentUserId === worklog.actor_detail?.id;
        const isExpanded = expandedId === worklog.id;

        return (
          <div key={worklog.id} className="flex flex-col gap-2 rounded-md border border-subtle bg-surface-2 p-3">
            <div className="flex items-start justify-between gap-2">
              <div className="flex min-w-0 items-start gap-2">
                <Avatar
                  src={worklog.actor_detail?.avatar_url}
                  name={worklog.actor_detail?.display_name || worklog.actor_detail?.first_name}
                  size="sm"
                />
                <div className="flex min-w-0 flex-col gap-0.5">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium text-primary">
                      {worklog.actor_detail?.display_name ||
                        `${worklog.actor_detail?.first_name} ${worklog.actor_detail?.last_name}`}
                    </span>
                    <span className="text-xs text-text-secondary">{formatDate(worklog.created_at)}</span>
                  </div>
                  {worklog.description && <p className="text-sm text-text-secondary truncate">{worklog.description}</p>}
                </div>
              </div>
              <div className="flex items-center gap-1">
                <span className="bg-surface-3 text-xs flex items-center gap-1 rounded-md px-2 py-1 font-medium text-primary">
                  <Clock className="h-3 w-3" />
                  {formatDuration(worklog.duration)}
                </span>
                {isOwn && (
                  <div className="relative">
                    <button
                      className="hover:bg-surface-3 flex items-center rounded p-1"
                      onClick={() => setExpandedId(isExpanded ? null : worklog.id)}
                    >
                      <MoreHorizontal className="text-text-secondary h-4 w-4" />
                    </button>
                    {isExpanded && (
                      <div className="shadow-md absolute top-full right-0 z-10 mt-1 w-32 rounded-md border border-subtle bg-surface-1">
                        <button
                          className="text-sm flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-surface-2"
                          onClick={() => {
                            onEdit?.(worklog.id);
                            setExpandedId(null);
                          }}
                        >
                          <Pencil className="h-3.5 w-3.5" />
                          Edit
                        </button>
                        <button
                          className="text-sm text-status-danger flex w-full items-center gap-2 px-3 py-2 text-left hover:bg-surface-2"
                          onClick={() => {
                            onDelete?.(worklog.id);
                            setExpandedId(null);
                          }}
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                          Delete
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
