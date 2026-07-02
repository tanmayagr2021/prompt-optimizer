"use client";

import { useState, useMemo } from "react";
import { StatCard } from "./stat-card";
import { InsightCard } from "./insight-card";
import { TipCard } from "./tip-card";
import { EmptyState } from "./empty-state";
import { CopyButton } from "./copy-button";
import { cn, fmt, calcStats } from "@/lib/utils";
import { getContextualTip } from "@/lib/guidance";
import { GROQ_MODELS } from "@/lib/prompts";
import type { OptimizeResult } from "@/lib/types";

const EXAMPLES = [
  "Write me a blog post about AI",
  "Summarize this document for me",
  "Help me write an email to my team about the project deadline",
  "Explain machine learning in simple terms",
  "Create a marketing campaign for my new product",
];

export function OptimizerTab() {
  const [input, setInput]   = useState("");
  const [model, setModel]   = useState<string>(GROQ_MODELS[0]);
  const [result, setResult] = useState<OptimizeResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState("");

  const tip = useMemo(() => getContextualTip("optimizer", ""), []);

  const handleOptimize = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: input, model }),
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
    delta: rawStats.removed > 0 ? `-${fmt(rawStats.removed)} chars` : rawStats.removed < 0 ? `+${fmt(-rawStats.removed)} chars` : "Same",
    deltaGood: rawStats.removed >= 0,
    ratio: rawStats.origChars > 0 ? rawStats.optChars / rawStats.origChars : 1,
    pct: Math.round(rawStats.optChars / (rawStats.origChars || 1) * 100),
  } : null;

  const modeLabel = result
    ? result.mode.startsWith("ai")
      ? result.model ?? "AI"
      : "Rule-based"
    : "";

  const tokenCount = Math.ceil(input.length / 4);

  return (
    <div className="space-y-10 animate-fade-in">
      {tip && <TipCard tip={tip} />}

      {/* Editor canvas */}
      <div className="bg-surface-container-lowest dark:bg-[#25261f] p-8 md:p-12 border border-ink dark:border-[#3d3a38] rounded-xl paper-shadow relative">
        <div className="absolute top-6 left-6 flex gap-1.5">
          <span className="w-2 h-2 rounded-full bg-primary/20" />
          <span className="w-2 h-2 rounded-full bg-primary/20" />
          <span className="w-2 h-2 rounded-full bg-primary/20" />
        </div>

        <div className="max-w-3xl mx-auto space-y-6">
          <div className="flex items-center justify-between border-b border-ink dark:border-[#3d3a38] pb-4">
            <span className="font-serif text-headline-md text-on-surface/40 italic">Your prompt…</span>
            <span className="text-label-sm text-on-surface-variant/60 uppercase tracking-widest">
              {fmt(input.length)} chars · ~{fmt(tokenCount)} tokens
            </span>
          </div>

          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Begin crafting your instructions here… Use [[variables]] for dynamic injection."
            aria-label="Prompt to optimize"
            className="writing-surface w-full min-h-[280px] bg-transparent border-none focus:ring-0 p-0 font-sans text-body-lg leading-relaxed text-on-surface placeholder:text-outline-variant/40 resize-none"
          />

          {/* Example chips */}
          {!input && (
            <div className="flex flex-wrap gap-2">
              {EXAMPLES.map((ex) => (
                <button
                  key={ex}
                  onClick={() => setInput(ex)}
                  className="text-label-sm px-3 py-1 rounded-full border border-ink dark:border-[#3d3a38] text-on-surface-variant hover:border-primary hover:text-primary dark:hover:border-primary-fixed-dim transition-all"
                >
                  {ex.length > 40 ? ex.slice(0, 38) + "…" : ex}
                </button>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between border-t border-ink dark:border-[#3d3a38] pt-6">
            <div className="flex items-center gap-4">
              <button
                onClick={() => { setInput(""); setResult(null); setError(""); }}
                className="flex items-center gap-2 text-label-sm uppercase tracking-wider text-on-surface-variant hover:text-primary transition-colors"
              >
                <span className="material-symbols-outlined text-sm">close</span> Clear
              </button>

              {/* Model selector */}
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="bg-transparent border-none text-label-sm text-on-surface-variant/60 cursor-pointer outline-none hover:text-on-surface transition-colors"
                title="Select model"
                aria-label="Select AI model"
              >
                {GROQ_MODELS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <button
              onClick={handleOptimize}
              disabled={!input.trim() || loading}
              className={cn(
                "flex items-center gap-3 px-10 py-3.5 rounded-lg font-sans text-label-sm tracking-[0.2em] uppercase transition-all shadow-sm",
                !input.trim() || loading
                  ? "bg-surface-container text-on-surface-variant/40 cursor-not-allowed"
                  : "bg-primary-container text-on-primary hover:scale-[1.02] active:scale-95 hover:shadow-md",
              )}
            >
              {loading ? (
                <>
                  <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Optimising…
                </>
              ) : (
                <>
                  Engineer Prompt
                  <span className="material-symbols-outlined text-base">bolt</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div role="alert" className="flex items-start gap-3 p-4 rounded-lg border border-error/30 bg-error-container/20 text-on-error-container text-sm">
          <span className="material-symbols-outlined text-error text-base mt-0.5">error</span>
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-fade-in">
          <div className="flex items-baseline justify-between mb-2">
            <h2 className="font-serif text-headline-md text-on-surface">Optimised Prompt</h2>
            <div className="flex items-center gap-3">
              <span className="text-label-sm uppercase tracking-widest text-on-surface-variant/60">
                {modeLabel}
              </span>
              <CopyButton text={result.optimized} />
            </div>
          </div>

          {/* Output canvas */}
          <div className="vellum-surface dark:bg-[#232420] border border-ink dark:border-[#3d3a38] rounded-xl p-8 md:p-10">
            <pre className="font-sans text-body-md text-on-surface leading-relaxed whitespace-pre-wrap break-words">
              {result.optimized}
            </pre>
          </div>

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-3 gap-4">
              <StatCard value={fmt(stats.originalLen)} label="Original chars" />
              <StatCard value={fmt(stats.optimizedLen)} label="Optimised chars" delta={stats.delta} deltaGood={stats.deltaGood} />
              <StatCard value={`${stats.pct}%`} label="Efficiency ratio" delta={stats.ratio <= 1 ? "Compressed" : "Expanded"} deltaGood={stats.ratio <= 1} />
            </div>
          )}

          {/* Insights */}
          {result.insights && result.insights.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-6">
                <h3 className="font-serif text-headline-md text-on-surface">Analysis &amp; Optimisation</h3>
                <span className="text-label-sm uppercase text-on-surface-variant/60">What changed &amp; why</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {result.insights.map((insight, i) => (
                  <InsightCard key={i} insight={insight} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {!result && !loading && (
        <EmptyState
          icon="✒️"
          title="Your optimised prompt will appear here"
          body="Paste any prompt above and click 'Engineer Prompt'. The AI will restructure it for maximum clarity, specificity, and model compatibility."
        />
      )}
    </div>
  );
}
