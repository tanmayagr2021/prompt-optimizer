"use client";

import { useState } from "react";
import { Wand2, Sparkles, AlertCircle } from "lucide-react";
import { StatCard } from "./stat-card";
import { InsightCard } from "./insight-card";
import { TipCard } from "./tip-card";
import { EmptyState } from "./empty-state";
import { CopyButton } from "./copy-button";
import { cn, fmt, calcStats, estimateTokens } from "@/lib/utils";
import { getContextualTip } from "@/lib/guidance";
import type { OptimizeResult } from "@/lib/types";

const EXAMPLES = [
  "Write me a blog post about AI",
  "Summarize this document for me",
  "Help me write an email to my team about the project deadline",
  "Explain machine learning to me",
  "Create a marketing campaign for my new product",
];

export function OptimizerTab() {
  const [input, setInput]   = useState("");
  const [result, setResult] = useState<OptimizeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  const tip = getContextualTip("optimizer", "");

  const handleOptimize = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Optimization failed");
      setResult(data as OptimizeResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const rawStats = result ? calcStats(input, result.optimized) : null;
  const stats = rawStats ? {
    originalLen:  rawStats.origChars,
    optimizedLen: rawStats.optChars,
    delta: rawStats.removed > 0 ? `-${fmt(rawStats.removed)} chars` : rawStats.removed < 0 ? `+${fmt(-rawStats.removed)} chars` : "Same length",
    deltaGood: rawStats.removed >= 0,
    ratio: rawStats.origChars > 0 ? rawStats.optChars / rawStats.origChars : 1,
    pct: Math.round(rawStats.optChars / (rawStats.origChars || 1) * 100),
  } : null;

  return (
    <div className="space-y-6">
      {tip && (
        <TipCard tip={tip} />
      )}

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Input */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Your Prompt
            </label>
            <div className="flex items-center gap-2">
              <span className="text-[0.7rem] text-gray-400">{fmt(input.length)} chars</span>
              <button
                onClick={() => setInput("")}
                className="text-[0.7rem] text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
              >
                Clear
              </button>
            </div>
          </div>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Paste or type your prompt here…"
            className={cn(
              "w-full h-56 resize-none rounded-xl border px-4 py-3 text-sm",
              "font-mono leading-relaxed bg-white dark:bg-gray-900",
              "border-gray-200 dark:border-gray-700",
              "text-gray-800 dark:text-gray-200",
              "placeholder:text-gray-400 dark:placeholder:text-gray-600",
              "focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent",
              "transition-all",
            )}
          />

          {/* Example chips */}
          {!input && (
            <div className="flex flex-wrap gap-1.5">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setInput(ex)}
                  className={cn(
                    "text-[0.7rem] px-2.5 py-1 rounded-full border",
                    "border-gray-200 dark:border-gray-700",
                    "text-gray-500 dark:text-gray-400",
                    "hover:border-indigo-400 hover:text-indigo-600 dark:hover:border-indigo-600 dark:hover:text-indigo-400",
                    "transition-all",
                  )}
                >
                  {ex.length > 40 ? ex.slice(0, 38) + "…" : ex}
                </button>
              ))}
            </div>
          )}

          <button
            onClick={handleOptimize}
            disabled={!input.trim() || loading}
            className={cn(
              "w-full py-2.5 rounded-xl font-semibold text-sm flex items-center justify-center gap-2",
              "transition-all duration-200",
              !input.trim() || loading
                ? "bg-gray-100 dark:bg-gray-800 text-gray-400 cursor-not-allowed"
                : "bg-indigo-600 hover:bg-indigo-700 text-white shadow-sm hover:shadow-md active:scale-[0.98]",
            )}
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Optimizing…
              </>
            ) : (
              <>
                <Wand2 size={15} />
                Optimize Prompt
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

        {/* Output */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Optimized Prompt
            </label>
            {result && (
              <div className="flex items-center gap-2">
                <span className={cn(
                  "text-[0.65rem] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full",
                  result.mode === "ai"
                    ? "bg-indigo-100 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400"
                    : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400",
                )}>
                  <Sparkles size={9} className="inline mr-0.5" />
                  {result.mode === "ai" ? result.model ?? "AI" : "Rule-based"}
                </span>
                <CopyButton text={result.optimized} />
              </div>
            )}
          </div>

          {result ? (
            <div className={cn(
              "h-56 overflow-auto rounded-xl border px-4 py-3",
              "border-emerald-200 dark:border-emerald-800 bg-emerald-50/50 dark:bg-emerald-950/20",
              "text-sm font-mono text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap",
            )}>
              {result.optimized}
            </div>
          ) : (
            <EmptyState
              icon="✨"
              title="Your optimized prompt will appear here"
              body="Paste any prompt on the left and click Optimize. The AI will restructure it for maximum clarity, specificity, and model compatibility."
              className="h-56"
            />
          )}

          {/* Stats row */}
          {stats && (
            <div className="grid grid-cols-3 gap-2">
              <StatCard
                value={fmt(stats.originalLen)}
                label="Original chars"
              />
              <StatCard
                value={fmt(stats.optimizedLen)}
                label="Optimized chars"
                delta={stats.delta}
                deltaGood={stats.deltaGood}
              />
              <StatCard
                value={`${stats.pct}%`}
                label="Efficiency ratio"
                delta={stats.ratio < 1 ? "Compressed" : "Expanded"}
                deltaGood={stats.ratio <= 1}
              />
            </div>
          )}
        </div>
      </div>

      {/* Insights */}
      {result?.insights && result.insights.length > 0 && (
        <div>
          <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">
            What changed &amp; why
          </h3>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
            {result.insights.map((insight, i) => (
              <InsightCard key={i} insight={insight} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
