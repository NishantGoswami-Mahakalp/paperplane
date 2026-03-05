/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import { useState } from "react";
import { Clock } from "lucide-react";
import { Button } from "@plane/propel/button";
import { ModalCore } from "../modals/modal-core";
import { EModalWidth } from "../modals/constants";

interface ManualWorklogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { description: string; duration: number; started_at: string }) => Promise<void>;
}

const DURATION_PRESETS = [
  { label: "15m", value: 15 },
  { label: "30m", value: 30 },
  { label: "1h", value: 60 },
  { label: "2h", value: 120 },
  { label: "4h", value: 240 },
];

export function ManualWorklogModal({ isOpen, onClose, onSubmit }: ManualWorklogModalProps) {
  const [description, setDescription] = useState("");
  const [duration, setDuration] = useState<number>(30);
  const [startedAt, setStartedAt] = useState(() => {
    const now = new Date();
    now.setHours(now.getHours() - 1);
    return now.toISOString().slice(0, 16);
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onSubmit({
        description,
        duration,
        started_at: new Date(startedAt).toISOString(),
      });
      setDescription("");
      setDuration(30);
      onClose();
    } catch (error) {
      console.error("Failed to create worklog:", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <ModalCore isOpen={isOpen} handleClose={onClose} width={EModalWidth.SM}>
      <div className="flex flex-col gap-4 p-4">
        <div className="flex items-center gap-2">
          <Clock className="text-text-secondary h-5 w-5" />
          <h2 className="text-lg font-semibold">Log Time</h2>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-text-secondary">Duration</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              min="1"
              value={duration}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setDuration(parseInt(e.target.value, 10) || 0)}
              className="w-24 rounded-md border border-subtle bg-surface-2 px-3 py-2 text-sm outline-none focus:border-accent-primary"
            />
            <span className="text-text-secondary">minutes</span>
          </div>
          <div className="flex flex-wrap gap-1">
            {DURATION_PRESETS.map((preset) => (
              <button
                key={preset.value}
                type="button"
                onClick={() => setDuration(preset.value)}
                className={`rounded-md px-2 py-1 text-xs font-medium transition-colors ${
                  duration === preset.value
                    ? "bg-accent-primary text-white"
                    : "bg-surface-2 text-text-secondary hover:bg-surface-3"
                }`}
              >
                {preset.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-text-secondary">Started At</label>
          <input
            type="datetime-local"
            value={startedAt}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStartedAt(e.target.value)}
            className="rounded-md border border-subtle bg-surface-2 px-3 py-2 text-sm outline-none focus:border-accent-primary"
          />
        </div>

        <div className="flex flex-col gap-2">
          <label className="text-sm font-medium text-text-secondary">Description (optional)</label>
          <textarea
            value={description}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setDescription(e.target.value)}
            placeholder="What did you work on?"
            className="min-h-[80px] w-full rounded-md border border-subtle bg-surface-2 p-2 text-sm outline-none focus:border-accent-primary"
          />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubmit} loading={isSubmitting}>
            Log Time
          </Button>
        </div>
      </div>
    </ModalCore>
  );
}
