/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState, useEffect } from "react";
import { observer } from "mobx-react";
import { WorkLogList } from "@plane/ui";
import { Clock } from "lucide-react";

interface WorkLogData {
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

type TIssueActivityWorklog = {
  workspaceSlug: string;
  projectId: string;
  issueId: string;
  ends?: "top" | "bottom";
};

export const IssueActivityWorklog = observer(function IssueActivityWorklog({
  workspaceSlug,
  projectId,
  issueId,
}: TIssueActivityWorklog) {
  const [worklogs, setWorklogs] = useState<WorkLogData[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const fetchWorklogs = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `/api/workspaces/${workspaceSlug}/projects/${projectId}/issues/${issueId}/worklogs/`
        );
        if (response.ok) {
          const data = await response.json();
          setWorklogs(data || []);
        }
      } catch (error) {
        console.error("Failed to fetch worklogs:", error);
        setWorklogs([]);
      } finally {
        setIsLoading(false);
      }
    };

    fetchWorklogs();
  }, [workspaceSlug, projectId, issueId]);

  const handleEdit = (worklogId: string) => {
    console.log("Edit worklog:", worklogId);
  };

  const handleDelete = (worklogId: string) => {
    console.log("Delete worklog:", worklogId);
  };

  const handleStartTimer = () => {
    console.log("Start timer for issue:", issueId);
  };

  if (isLoading) {
    return (
      <div className="text-text-secondary flex items-center gap-2 p-2">
        <Clock className="h-4 w-4 animate-spin" />
        <span className="text-sm">Loading worklogs...</span>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <WorkLogList worklogs={worklogs} onEdit={handleEdit} onDelete={handleDelete} onStartTimer={handleStartTimer} />
    </div>
  );
});
