/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState, useCallback, useEffect } from "react";
import { observer } from "mobx-react";
import type { TIssueServiceType } from "@plane/types";
import { EIssueServiceType } from "@plane/types";
import { TimerWidget } from "@plane/ui";
import { useUser } from "@/hooks/store/user";

type TIssueWorklogProperty = {
  workspaceSlug: string;
  projectId: string;
  issueId: string;
  disabled: boolean;
  issueServiceType?: TIssueServiceType;
};

interface ActiveTimer {
  issueId: string;
  startTime: Date;
  workspaceSlug: string;
}

export const IssueWorklogProperty = observer(function IssueWorklogProperty({
  workspaceSlug,
  projectId,
  issueId,
  disabled,
  issueServiceType = EIssueServiceType.ISSUES,
}: TIssueWorklogProperty) {
  const { data: currentUser } = useUser();

  const [activeTimer, setActiveTimer] = useState<ActiveTimer | null>(null);
  const [showWarning, setShowWarning] = useState(false);
  const [warningMessage, setWarningMessage] = useState("");

  useEffect(() => {
    const handleStorageChange = () => {
      const timerData = localStorage.getItem("active_timer");
      if (timerData) {
        const parsed = JSON.parse(timerData);
        if (parsed.issueId !== issueId && parsed.userId === currentUser?.id) {
          setShowWarning(true);
          setWarningMessage(
            `Timer is running on another issue (${parsed.issueId}). Stop it first to start a new timer.`
          );
        }
      } else {
        setShowWarning(false);
        setWarningMessage("");
      }
    };

    handleStorageChange();
    window.addEventListener("storage", handleStorageChange);
    const interval = setInterval(handleStorageChange, 5000);

    return () => {
      window.removeEventListener("storage", handleStorageChange);
      clearInterval(interval);
    };
  }, [issueId, currentUser?.id]);

  const handleStartTimer = useCallback(() => {
    const timerData = {
      issueId,
      projectId,
      workspaceSlug,
      userId: currentUser?.id,
      startTime: new Date().toISOString(),
    };
    localStorage.setItem("active_timer", JSON.stringify(timerData));
    setActiveTimer({
      issueId,
      startTime: new Date(),
      workspaceSlug,
    });
    setShowWarning(false);
    setWarningMessage("");
  }, [issueId, projectId, workspaceSlug, currentUser?.id]);

  const handleStopTimer = useCallback(() => {
    const timerData = localStorage.getItem("active_timer");
    if (timerData) {
      const parsed = JSON.parse(timerData);
      if (parsed.issueId === issueId) {
        localStorage.removeItem("active_timer");
        setActiveTimer(null);
      }
    }
  }, [issueId]);

  const isRunning = activeTimer?.issueId === issueId;

  return (
    <div className="flex flex-col gap-2">
      <TimerWidget
        isRunning={isRunning}
        startTime={activeTimer?.startTime || null}
        onStart={handleStartTimer}
        onStop={handleStopTimer}
        disabled={disabled}
        showWarning={showWarning}
        warningMessage={warningMessage}
      />
    </div>
  );
});
