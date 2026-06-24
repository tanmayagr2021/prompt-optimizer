"use client";

import { useState } from "react";
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

  return (
    <div className="space-y-10 animate-fade-in">
      {tip && <TipCard tip={tip} />}

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Left: Configuration */}
        <aside className="space-y-8">
          <div>
            <h3 className="text-label-sm uppercase tracking-[0.2em] text-on-surface-variant/60 mb-5">Configuration</h3>
            <div className="space-y-6">
              {/* Model */}
              <div>
                <label className="text-label-sm uppercase text-on-surface-variant block mb-2">Large Language Model</label>
                <select
                  value={model}
                  onChange={(e) => setModel(e.target.value)}
                  className="w-full bg-surface-container-low dark:bg-[#232420] border-b border-outline-variant/50 p-3 font-sans text-sm text-on-surface focus:border-primary-container transition-colors appearance-none cursor-pointer rounded-none outline-none"
                >
                  {GROQ_MODELS.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
              </div>

              {/* Platform */}
              <div>
                <label className="text-label-sm uppercase text-on-surface-variant block mb-3">Target Platform</label>
                <div className="flex flex-wrap gap-2">
                  {PLATFORMS.map((p) => {
                    const meta = PLATFORM_META[p];
                    return (
                      <button
                        key={p}
                        onClick={() => setPlatform(p)}
                        className={cn(
                          "inline-flex items-center gap-1 px-3 py-1.5 rounded text-xs font-medium border transition-all",
                          platform === p
                            ? "border-primary bg-primary-container text-on-primary"
                            : "border-ink dark:border-[#3d3a38] text-on-surface-variant hover:border-primary hover:text-primary dark:hover:border-primary-fixed-dim",
                        )}
                      >
                        {meta.icon} {p}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>

          {/* Studio context card */}
          <div className="luxury-card p-6 rounded-xl space-y-4">
            <h4 className="font-serif text-headline-md text-on-surface">Studio Context</h4>
            <p className="text-sm text-on-surface-variant italic">"Precision is the byproduct of intentional silence."</p>
            <div className="editorial-rule" />
            <p className="text-xs text-on-surface-variant/70">
              The 7-phase architect pipeline analyses intent, resolves contradictions, injects platform-specific patterns, and scores the output across 6 dimensions.
            </p>
          </div>
        </aside>

        {/* Right: Input + Output */}
        <section className="space-y-6">
          {/* Writing canvas */}
          <div className="bg-surface-container-lowest dark:bg-[#25261f] p-8 border border-ink dark:border-[#3d3a38] rounded-xl paper-shadow">
            <input
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder="Describe your task in plain language..."
              className="w-full font-serif text-headline-md bg-transparent border-none focus:ring-0 mb-6 p-0 text-on-surface placeholder:text-outline-variant/40 outline-none"
            />
            <textarea
              value={request}
              onChange={(e) => setRequest(e.target.value)}
              placeholder={`e.g. "Analyze a Python codebase for security vulnerabilities and produce an editorial-style audit report for ${platform}"`}
              className="writing-surface w-full min-h-[160px] bg-transparent border-none focus:ring-0 p-0 font-sans text-body-md leading-relaxed text-on-surface placeholder:text-outline-variant/30 resize-none"
            />
            <div className="border-t border-ink dark:border-[#3d3a38] pt-5 flex justify-end">
              <button
                onClick={handleGenerate}
                disabled={!request.trim() || loading}
                className={cn(
                  "flex items-center gap-3 px-10 py-3.5 rounded-lg font-sans text-label-sm tracking-[0.2em] uppercase transition-all",
                  !request.trim() || loading
                    ? "bg-surface-container text-on-surface-variant/40 cursor-not-allowed"
                    : "bg-primary-container text-on-primary hover:scale-[1.02] active:scale-95 shadow-sm hover:shadow-md",
                )}
              >
                {loading ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Architecting…
                  </>
                ) : (
                  <>
                    Architect Prompt
                    <span className="material-symbols-outlined text-base">architecture</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {error && (
            <div className="flex items-start gap-3 p-4 rounded-lg border border-error/30 bg-error-container/20 text-sm">
              <span className="material-symbols-outlined text-error text-base mt-0.5">error</span>
              {error}
            </div>
          )}
        </section>
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-8 animate-fade-in">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Intent card */}
            <div className="bg-surface-container-low dark:bg-[#232420] p-8 border border-outline-variant/30 rounded-lg hover:shadow-card transition-shadow">
              <div className="flex items-center gap-3 mb-5">
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>psychology</span>
                <h4 className="text-label-sm uppercase tracking-widest text-on-surface">Intent Analysis</h4>
              </div>
              <p className="text-sm text-on-surface-variant leading-relaxed line-clamp-4">{result.analysis || "Platform-specific prompt architecture applied."}</p>
              {result.total > 0 && (
                <div className="mt-5 pt-5 border-t border-outline-variant/20">
                  <div className="w-full h-1 bg-outline-variant/30 rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full transition-all duration-700" style={{ width: `${result.total}%` }} />
                  </div>
                  <span className="text-[10px] uppercase text-on-surface-variant mt-1.5 block">Quality Score: {result.total}%</span>
                </div>
              )}
            </div>

            {/* Enhancements card */}
            <div className="bg-surface-container-low dark:bg-[#232420] p-8 border border-outline-variant/30 rounded-lg hover:shadow-card transition-shadow">
              <div className="flex items-center gap-3 mb-5">
                <span className="material-symbols-outlined text-secondary" style={{ fontVariationSettings: "'FILL' 1" }}>layers</span>
                <h4 className="text-label-sm uppercase tracking-widest text-on-surface">Enhancements</h4>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {(result.enhancements || "").split("\n").filter(Boolean).slice(0, 6).map((e, i) => (
                  <span key={i} className="px-2 py-0.5 bg-secondary-fixed text-on-secondary-fixed text-[10px] font-bold uppercase rounded tracking-tight">
                    {e.replace(/^[-•*]\s*/, "").slice(0, 30)}
                  </span>
                ))}
              </div>
            </div>

            {/* Score card */}
            {result.total > 0 && (
              <div className="bg-primary text-on-primary p-8 border border-primary-container rounded-lg hover:scale-[1.01] transition-transform">
                <div className="flex items-center gap-3 mb-5">
                  <span className="material-symbols-outlined">verified</span>
                  <h4 className="text-label-sm uppercase tracking-widest">Efficiency Rating</h4>
                </div>
                <div className="flex items-end gap-2 mb-3">
                  <span className="font-serif text-5xl font-bold">{result.total}</span>
                  <span className="font-serif text-xl opacity-60 mb-1">/100</span>
                </div>
                <p className="text-sm text-on-primary-container">
                  {result.total >= 80 ? "Highly optimized prompt." : "Good — minor improvements possible."}
                </p>
              </div>
            )}
          </div>

          {/* Generated prompt */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-serif text-headline-md text-on-surface">Generated Prompt</h3>
              <CopyButton text={result.prompt} />
            </div>
            <div className="vellum-surface dark:bg-[#232420] border border-ink dark:border-[#3d3a38] rounded-xl p-8 max-h-80 overflow-auto">
              <pre className="font-sans text-body-md text-on-surface leading-relaxed whitespace-pre-wrap break-words">
                {result.prompt}
              </pre>
            </div>
          </div>
        </div>
      )}

      {!result && !loading && (
        <EmptyState
          icon="🏗️"
          title="Your architected prompt will appear here"
          body={`Describe your task and select a target platform. The 7-phase AI pipeline will craft a production-ready prompt optimized for ${platform}.`}
        />
      )}
    </div>
  );
}
