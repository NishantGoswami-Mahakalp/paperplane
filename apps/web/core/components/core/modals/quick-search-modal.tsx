/**
 * Copyright (c) 2023-present Plane Software, Inc. and contributors
 * SPDX-License-Identifier: AGPL-3.0-only
 * See the LICENSE file for details.
 */

import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { observer } from "mobx-react";
import { Command } from "cmdk";
import { Dialog, Transition } from "@headlessui/react";
import { HelpCircle, ArrowUp, ArrowDown, CornerDownLeft, SearchIcon, Clock, X } from "lucide-react";
import { useTranslation } from "@plane/i18n";
import { cn } from "@plane/utils";
import type { IWorkspaceIssueSearchResult } from "@plane/types";
import { Loader, Badge } from "@plane/ui";
import { useAppRouter } from "@/hooks/use-app-router";
import useDebounce from "@/hooks/use-debounce";
import { WorkspaceService } from "@/services/workspace.service";

interface QuickSearchState {
  isOpen: boolean;
  open: () => void;
  close: () => void;
  toggle: () => void;
}

const QuickSearchContext = createContext<QuickSearchState | null>(null);

const DEFAULT_QUICK_SEARCH_STATE: QuickSearchState = {
  isOpen: false,
  open: () => {},
  close: () => {},
  toggle: () => {},
};

export const useQuickSearchContext = (): QuickSearchState => {
  const context = useContext(QuickSearchContext);
  if (!context) {
    return DEFAULT_QUICK_SEARCH_STATE;
  }
  return context;
};

interface QuickSearchProviderProps {
  children: React.ReactNode;
}

export const QuickSearchProvider: React.FC<QuickSearchProviderProps> = observer(({ children }) => {
  const [isOpen, setIsOpen] = useState(false);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((prev) => !prev), []);

  const value = useMemo(() => ({ isOpen, open, close, toggle }), [isOpen, open, close, toggle]);

  return <QuickSearchContext.Provider value={value}>{children}</QuickSearchContext.Provider>;
});

const workspaceService = new WorkspaceService();

const RECENT_SEARCHES_KEY = "plane_recent_issue_searches";
const MAX_RECENT_SEARCHES = 5;

function getRecentSearches(): IWorkspaceIssueSearchResult[] {
  if (typeof window === "undefined") return [];
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveRecentSearch(issue: IWorkspaceIssueSearchResult): void {
  if (typeof window === "undefined") return;
  try {
    const existing = getRecentSearches();
    const filtered = existing.filter((i) => i.id !== issue.id);
    const updated = [issue, ...filtered].slice(0, MAX_RECENT_SEARCHES);
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
  } catch {
    // ignore
  }
}

function clearRecentSearches(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(RECENT_SEARCHES_KEY);
}

interface QuickSearchModalProps {
  workspaceSlug: string;
}

export const QuickSearchModal = observer(function QuickSearchModal({ workspaceSlug }: QuickSearchModalProps) {
  const { t } = useTranslation();
  const router = useAppRouter();
  const [searchTerm, setSearchTerm] = useState("");
  const [results, setResults] = useState<IWorkspaceIssueSearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [recentSearches, setRecentSearches] = useState<IWorkspaceIssueSearchResult[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const commandRef = useRef<HTMLDivElement>(null);

  const { isOpen, close } = useQuickSearchContext();

  const debouncedSearch = useDebounce(searchTerm, 300);

  useEffect(() => {
    if (isOpen && commandRef.current) {
      const input = commandRef.current.querySelector("[cmdk-input]") as HTMLInputElement;
      if (input) {
        setTimeout(() => input.focus(), 50);
      }
    }
  }, [isOpen]);

  useEffect(() => {
    setRecentSearches(getRecentSearches());
  }, [isOpen]);

  useEffect(() => {
    const searchIssues = async () => {
      if (!debouncedSearch || debouncedSearch.length < 2) {
        setResults([]);
        return;
      }

      setIsLoading(true);
      try {
        const response = await workspaceService.searchWorkspace(workspaceSlug, {
          search: debouncedSearch,
          workspace_search: true,
        });
        setResults(response.results.issue || []);
      } catch (error) {
        console.error("Search error:", error);
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    };

    searchIssues();
  }, [debouncedSearch, workspaceSlug]);

  const groupedResults = useMemo(() => {
    const groups: Record<string, IWorkspaceIssueSearchResult[]> = {};
    results.forEach((issue) => {
      const key = issue.project__identifier;
      if (!groups[key]) {
        groups[key] = [];
      }
      groups[key].push(issue);
    });
    return groups;
  }, [results]);

  const flatResults = useMemo(() => {
    if (searchTerm.length < 2) {
      return recentSearches;
    }
    return results;
  }, [searchTerm, results, recentSearches]);

  const handleSelect = useCallback(
    (issue: IWorkspaceIssueSearchResult) => {
      saveRecentSearch(issue);
      close();
      router.push(`/${workspaceSlug}/projects/${issue.project_id}/issues/${issue.id}`);
    },
    [close, router, workspaceSlug]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      const maxIndex = flatResults.length - 1;

      if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, maxIndex));
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (flatResults[selectedIndex]) {
          handleSelect(flatResults[selectedIndex]);
        }
      }
    },
    [flatResults, selectedIndex, handleSelect]
  );

  useEffect(() => {
    setSelectedIndex(0);
  }, [searchTerm, results]);

  const handleClose = useCallback(() => {
    setSearchTerm("");
    setResults([]);
    setSelectedIndex(0);
    close();
  }, [close]);

  return (
    <Transition.Root show={isOpen} as="div">
      <Dialog as="div" className="relative z-50" onClose={handleClose}>
        <Transition.Child
          as="div"
          enter="ease-out duration-200"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-150"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-backdrop/50" />
        </Transition.Child>

        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex min-h-full items-start justify-center p-4 pt-[15vh]">
            <Transition.Child
              as="div"
              enter="ease-out duration-200"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-150"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="shadow-xl w-full max-w-xl transform overflow-hidden rounded-lg bg-surface-1 transition-all">
                <div className="relative border-b border-subtle-1">
                  <SearchIcon className="absolute top-1/2 left-3 size-5 -translate-y-1/2 text-placeholder" />
                  <Command ref={commandRef} shouldFilter={false} className="w-full" onKeyDown={handleKeyDown}>
                    <Command.Input
                      value={searchTerm}
                      onValueChange={setSearchTerm}
                      placeholder={t("common.quick_search.placeholder") || "Search issues..."}
                      className="text-15 w-full border-0 bg-transparent py-4 pr-10 pl-10 text-primary placeholder:text-placeholder focus:ring-0 focus:outline-none"
                    />
                  </Command>
                  {searchTerm && (
                    <button
                      onClick={() => setSearchTerm("")}
                      className="absolute top-1/2 right-3 -translate-y-1/2 text-placeholder hover:text-primary"
                    >
                      <X className="size-4" />
                    </button>
                  )}
                </div>

                <div className="max-h-[60vh] overflow-y-auto">
                  {isLoading ? (
                    <div className="flex items-center justify-center py-10">
                      <Loader className="space-y-3">
                        <Loader.Item className="h-4 w-3/4 rounded" />
                        <Loader.Item className="h-4 w-1/2 rounded" />
                      </Loader>
                    </div>
                  ) : searchTerm.length < 2 ? (
                    <div className="py-4">
                      {recentSearches.length > 0 && (
                        <div className="px-3">
                          <div className="mb-2 flex items-center justify-between px-2">
                            <span className="text-xs font-medium text-secondary">
                              {t("common.quick_search.recent") || "Recent"}
                            </span>
                            <button onClick={clearRecentSearches} className="text-xs text-secondary hover:text-primary">
                              {t("common.quick_search.clear") || "Clear"}
                            </button>
                          </div>
                          {recentSearches.map((issue, index) => (
                            <button
                              key={issue.id}
                              onClick={() => handleSelect(issue)}
                              className={cn(
                                "flex w-full items-center gap-3 rounded px-3 py-2 text-left transition-colors hover:bg-layer-2",
                                selectedIndex === index && "bg-layer-2"
                              )}
                            >
                              <Clock className="size-4 shrink-0 text-secondary" />
                              <div className="min-w-0 flex-1 truncate">
                                <span className="text-sm text-primary">{issue.name}</span>
                              </div>
                              <Badge variant="neutral" className="text-xs shrink-0">
                                {issue.project__identifier}-{issue.sequence_id}
                              </Badge>
                            </button>
                          ))}
                        </div>
                      )}
                      {recentSearches.length === 0 && (
                        <div className="px-4 py-8 text-center">
                          <p className="text-sm text-secondary">
                            {t("common.quick_search.hint") || "Type at least 2 characters to search"}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : results.length === 0 ? (
                    <div className="px-4 py-8 text-center">
                      <HelpCircle className="mx-auto mb-2 size-8 text-secondary" />
                      <p className="text-sm text-secondary">
                        {t("common.quick_search.no_results") || "No issues found"}
                      </p>
                    </div>
                  ) : (
                    <div className="py-2">
                      {Object.entries(groupedResults).map(([projectIdentifier, issues]) => (
                        <div key={projectIdentifier} className="mb-2">
                          <div className="sticky top-0 z-10 bg-surface-1 px-3 py-1.5">
                            <span className="text-xs font-semibold text-secondary">{projectIdentifier}</span>
                          </div>
                          {issues.map((issue) => {
                            const globalIndex = flatResults.findIndex((r) => r.id === issue.id);
                            return (
                              <button
                                key={issue.id}
                                onClick={() => handleSelect(issue)}
                                className={cn(
                                  "flex w-full items-center gap-3 px-3 py-2 text-left transition-colors hover:bg-layer-2",
                                  selectedIndex === globalIndex && "bg-layer-2"
                                )}
                              >
                                <div className="min-w-0 flex-1 truncate">
                                  <span className="text-sm text-primary">{issue.name}</span>
                                </div>
                                <Badge variant="neutral" className="text-xs shrink-0">
                                  #{issue.sequence_id}
                                </Badge>
                              </button>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <div className="text-xs flex items-center justify-between border-t border-subtle-1 bg-layer-2 px-4 py-2.5 text-secondary">
                  <div className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <ArrowUp className="size-3" />
                      <ArrowDown className="size-3" />
                      <span>{t("common.quick_search.navigate") || "Navigate"}</span>
                    </span>
                    <span className="flex items-center gap-1">
                      <CornerDownLeft className="size-3" />
                      <span>{t("common.quick_search.open") || "Open"}</span>
                    </span>
                  </div>
                  <span className="flex items-center gap-1">
                    <span className="font-mono rounded bg-layer-1 px-1.5 py-0.5 text-[10px]">Esc</span>
                    <span>{t("common.quick_search.close") || "Close"}</span>
                  </span>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition.Root>
  );
});
