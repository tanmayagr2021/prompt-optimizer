"use client";

import { useState } from "react";
import { Building2, AlertCircle, Star } from "lucide-react";
import { TipCard } from "./tip-card";
import { EmptyState } from "./empty-state";
import { CopyButton } from "./copy-button";
import { cn } from "@/lib/utils";
import { getContextualTip } from "@/lib/guidance";
import { PLATFORMS, PLATFORM_META, GROQ_MODELS } from "@/lib/prompts";
import type { ArchitectResult } from "@/lib/types";

const SCORE_LABELS = ["Specificity", "Structure", "AI Optimization", "Completeness", "Clarity", "Success Probability"];

export function ArchitectTab() {
  const [request, setRequest]   = useState("");
  const [platform, setPlatform] = useState<string>("Claude");
  const [model, setModel]       = useState<string>(GROQ_MODELS[0]);
  const [result, setResult]     = useState<ArchitectResult | null>(null);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const tip = getContextualTip("architect", platform);

  const handleGenerate = async () => {
    if (!request.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/architect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ userRequest: request, platform, model }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Generation failed");
      setResult(data as ArchitectResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const maxScore = Math.max(...Object.values(result?.scores ?? {}), 1);

  return (
    <div className="space-y-6">
      {tip && <TipCard tip={tip} />}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Left: Inputs */}
        <div className="space-y-4">
          <div>
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 block">
              What do you want to accomplish?
            </label>
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Describe your task in plain language. The AI will architect a production-ready prompt…"
              className={cn(
                "w-full h-44 resize-none rounded-xl border px-4 py-3 text-sm",
                "font-mono leading-relaxed bg-white dark:bg-gray-900",
                "border-gray-200 dark:border-gray-700",
                "text-gray-800 dark:text-gray-200",
                "placeholder:text-gray-400 dark:placeholder:text-gray-600",
                "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all",
              )}
            />
          </div>

          {/* Platform selector */}
          <div>
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 block">
              Target Platform
            </label>
            <div className="flex flex-wrap gap-1.5">
              {PLATFORMS.map((p) => {
                const meta = PLATFORM_META[p];
                return (
                  <button
                    key={p}
                    onClick={() => setPlatform(p)}
                    className={cn(
                      "inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium",
                      "border transition-all",
                      platform === p
                        ? "border-indigo-500 bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300"
                        : "border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-400 dark:hover:border-gray-600",
                    )}
                  >
                    <span>{meta.icon}</span> {p}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Model selector */}
          <div>
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 block">
              AI Model
            </label>
            <select
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className={cn(
                "w-full rounded-xl border px-3 py-2 text-sm bg-white dark:bg-gray-900",
                "border-gray-200 dark:border-gray-700 text-gray-800 dark:text-gray-200",
                "focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all",
              )}
            >
              {GROQ_MODELS.map((m) => (
                <option key={m} value={m}>{m}</option>
              ))}
            </select>
          </div>

          <button
            onClick={handleGenerate}
            disabled={!request.trim() || loading}
            className={cn(
              "w-full py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2",
              "transition-all duration-200",
              !request.trim() || loading
                ? "bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow-md active:scale-[0.98]",
            )}
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Architecting (7 phases)…
              </>
            ) : (
              <>
                <Building2 size={15} />
                Architect Prompt
              </>
            )}
          </button>

          {error && (
            <div className="flex items-start gap-2 p-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 text-xs">
              <AlertCircle size={13} className="mt-0.5 shrink-0" />
              {error}
            </div>
          )}
        </div>

        {/* Right: Results */}
        <div className="space-y-4">
          {result ? (
            <>
              {/* Quality score */}
              {result.total > 0 && (
                <div className="rounded-xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-950/20 p-4">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-xs font-bold text-indigo-700 dark:text-indigo-300 uppercase tracking-widest">
                      Quality Score
                    </span>
                    <span className="text-2xl font-extrabold text-indigo-600 dark:text-indigo-400">
                      {result.total}<span className="text-sm font-semibold text-indigo-400">/100</span>
                    </span>
                  </div>
                  {Object.entries(result.scores).length > 0 && (
                    <div className="space-y-1.5">
                      {SCORE_LABELS.filter((l) => result.scores[l] !== undefined).map((label) => {
                        const val = result.scores[label];
                        const pct = (val / 10) * 100;
                        return (
                          <div key={label} className="flex items-center gap-2">
                            <span className="text-[0.65rem] text-indigo-600 dark:text-indigo-400 w-28 shrink-0">{label}</span>
                            <div className="flex-1 h-1.5 bg-indigo-100 dark:bg-indigo-900/50 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-indigo-500 dark:bg-indigo-400 rounded-full transition-all duration-700"
                                style={{ width: `${pct}%` }}
                              />
                            </div>
                            <span className="text-[0.65rem] font-bold text-indigo-500 w-6 text-right">{val}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Generated prompt */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">Generated Prompt</span>
                  <CopyButton text={result.prompt} />
                </div>
                <div className={cn(
                  "rounded-xl border border-emerald-200 dark:border-emerald-800",
                  "bg-emerald-50/50 dark:bg-emerald-950/20 p-4",
                  "text-sm font-mono text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap",
                  "max-h-56 overflow-auto",
                )}>
                  {result.prompt}
                </div>
              </div>

              {/* Analysis */}
              {result.analysis && (
                <details className="group">
                  <summary className="cursor-pointer text-xs font-semibold text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
                    <span className="group-open:hidden">▶ Show analysis</span>
                    <span className="hidden group-open:inline">▼ Hide analysis</span>
                  </summary>
                  <div className="mt-2 text-[0.77rem] text-gray-600 dark:text-gray-400 leading-relaxed bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 whitespace-pre-wrap">
                    {result.analysis}
                  </div>
                </details>
              )}

              {/* Enhancements */}
              {result.enhancements && (
                <details className="group">
                  <summary className="cursor-pointer text-xs font-semibold text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition-colors">
                    <span className="group-open:hidden">▶ Show enhancements added</span>
                    <span className="hidden group-open:inline">▼ Hide enhancements added</span>
                  </summary>
                  <div className="mt-2 text-[0.77rem] text-gray-600 dark:text-gray-400 leading-relaxed bg-gray-50 dark:bg-gray-900/50 rounded-lg p-3 whitespace-pre-wrap">
                    {result.enhancements}
                  </div>
                </details>
              )}
            </>
          ) : (
            <EmptyState
              icon="🏗️"
              title="Your architected prompt will appear here"
              body={`Describe your task and select a target platform. The 7-phase AI pipeline will craft a production-ready prompt optimized specifically for ${platform}.`}
            />
          )}
        </div>
      </div>
    </div>
  );
}
