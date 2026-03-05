/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useEffect, useState, useCallback } from "react";
import { Play, Square, Clock } from "lucide-react";
import { Button } from "../button/button";

interface TimerWidgetProps {
  isRunning: boolean;
  startTime: Date | null;
  onStart: () => void;
  onStop: () => void;
  disabled?: boolean;
  showWarning?: boolean;
  warningMessage?: string;
}

const formatDuration = (seconds: number): string => {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }
  return `${minutes}:${secs.toString().padStart(2, "0")}`;
};

export function TimerWidget({
  isRunning,
  startTime,
  onStart,
  onStop,
  disabled = false,
  showWarning = false,
  warningMessage,
}: TimerWidgetProps) {
  const [elapsedSeconds, setElapsedSeconds] = useState(0);

  useEffect(() => {
    if (isRunning && startTime) {
      const calculateElapsed = () => {
        const now = new Date();
        const diff = Math.floor((now.getTime() - startTime.getTime()) / 1000);
        setElapsedSeconds(diff);
      };

      calculateElapsed();
      const interval = setInterval(calculateElapsed, 1000);

      return () => clearInterval(interval);
    } else {
      setElapsedSeconds(0);
    }
  }, [isRunning, startTime]);

  const handleStart = useCallback(() => {
    if (!disabled && !showWarning) {
      onStart();
    }
  }, [disabled, showWarning, onStart]);

  const handleStop = useCallback(() => {
    if (!disabled) {
      onStop();
    }
  }, [disabled, onStop]);

  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 rounded-md border border-subtle bg-surface-2 px-3 py-2">
          <Clock className="text-text-secondary h-4 w-4" />
          <span className="font-mono text-lg font-medium text-primary">{formatDuration(elapsedSeconds)}</span>
          {isRunning && (
            <span className="flex h-2 w-2">
              <span className="bg-status-success absolute inline-flex h-2 w-2 animate-ping rounded-full opacity-75" />
              <span className="bg-status-success relative inline-flex h-2 w-2 rounded-full" />
            </span>
          )}
        </div>
        {isRunning ? (
          <Button
            variant="danger"
            size="sm"
            onClick={handleStop}
            disabled={disabled}
            appendIcon={<Square className="h-3.5 w-3.5" />}
          >
            Stop
          </Button>
        ) : (
          <Button
            variant="primary"
            size="sm"
            onClick={handleStart}
            disabled={disabled || showWarning}
            prependIcon={<Play className="h-3.5 w-3.5" />}
          >
            Start
          </Button>
        )}
      </div>
      {showWarning && warningMessage && <p className="text-xs text-status-warning">{warningMessage}</p>}
    </div>
  );
}
