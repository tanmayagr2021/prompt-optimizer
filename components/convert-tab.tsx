"use client";

import { useState, useRef, useCallback } from "react";
import { StatCard } from "./stat-card";
import { CopyButton } from "./copy-button";
import { cn, fmt } from "@/lib/utils";
import type { InputFormat } from "@/lib/converters/index";

// ─── CONSTANTS ────────────────────────────────────────────────────────────────

const OUTPUT_FORMATS = [
  { id: "md",   label: "Markdown", icon: "article" },
  { id: "html", label: "HTML",     icon: "html" },
  { id: "docx", label: "Word",     icon: "description" },
  { id: "pdf",  label: "PDF",      icon: "picture_as_pdf" },
  { id: "txt",  label: "Text",     icon: "text_snippet" },
  { id: "csv",  label: "CSV",      icon: "table_chart" },
  { id: "json", label: "JSON",     icon: "data_object" },
  { id: "xml",  label: "XML",      icon: "code" },
] as const;

type OutputFmtId = typeof OUTPUT_FORMATS[number]["id"];

const AI_ACTIONS = [
  { id: "clean",     label: "Clean Formatting",  icon: "auto_fix_high" },
  { id: "summarize", label: "Summarize",          icon: "summarize" },
  { id: "notes",     label: "Convert to Notes",   icon: "edit_note" },
  { id: "readme",    label: "Generate README",    icon: "terminal" },
  { id: "actions",   label: "Extract Actions",    icon: "checklist" },
  { id: "explain",   label: "Explain",            icon: "lightbulb" },
  { id: "docs",      label: "To Documentation",   icon: "menu_book" },
  { id: "translate", label: "Translate",           icon: "translate" },
  { id: "grammar",   label: "Fix Grammar",         icon: "spellcheck" },
  { id: "study",     label: "Study Notes",         icon: "school" },
  { id: "blog",      label: "To Blog Post",        icon: "edit_square" },
  { id: "rewrite",   label: "Rewrite",             icon: "change_circle" },
] as const;

const ACCEPTED = ".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.csv,.md,.txt,.html,.epub,.json,.xml,.png,.jpg,.jpeg,.webp,.gif,.bmp";

const FORMAT_BADGES = ["PDF", "DOCX", "PPTX", "XLSX", "CSV", "MD", "HTML", "TXT", "EPUB", "JSON", "XML", "Image OCR"];

function fileSizeLabel(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

// ─── TYPES ────────────────────────────────────────────────────────────────────

interface ConvertResult {
  text: string;
  outputBase64: string;
  mimeType: string;
  ext: string;
  fileName: string;
  inputFormat: InputFormat;
  inputLabel: string;
  outputFormat: string;
  meta: Record<string, string>;
  stats: { inputChars: number; outputChars: number; inputWords: number; outputWords: number };
}

type Stage = "idle" | "ready" | "converting" | "done" | "enhancing" | "redownloading";

// ─── COMPONENT ────────────────────────────────────────────────────────────────

export function ConvertTab() {
  const [stage, setStage]           = useState<Stage>("idle");
  const [file, setFile]             = useState<File | null>(null);
  const [outputFormat, setOutput]   = useState<OutputFmtId>("md");
  const [aiAction, setAiAction]     = useState<string | null>(null);
  const [targetLang, setTargetLang] = useState("Spanish");
  const [result, setResult]         = useState<ConvertResult | null>(null);
  const [enhanced, setEnhanced]     = useState<string | null>(null);
  const [error, setError]           = useState("");
  const [dragging, setDragging]     = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);

  // ── File selection ──────────────────────────────────────────────────────────

  const selectFile = useCallback((f: File) => {
    setFile(f);
    setStage("ready");
    setResult(null);
    setEnhanced(null);
    setError("");
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) selectFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) selectFile(f);
  };

  const reset = () => {
    setFile(null);
    setStage("idle");
    setResult(null);
    setEnhanced(null);
    setError("");
    setAiAction(null);
    if (fileRef.current) fileRef.current.value = "";
  };

  // ── Conversion ──────────────────────────────────────────────────────────────

  const handleConvert = async () => {
    if (!file) return;
    setStage("converting");
    setError("");
    setEnhanced(null);

    const fd = new FormData();
    fd.append("file", file);
    fd.append("outputFormat", outputFormat);

    try {
      const res = await fetch("/api/convert", { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Conversion failed");
      setResult(data as ConvertResult);
      setStage("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setStage("ready");
    }
  };

  // ── AI Enhancement ──────────────────────────────────────────────────────────

  const handleEnhance = async () => {
    if (!result || !aiAction) return;
    setStage("enhancing");
    setError("");

    try {
      const res = await fetch("/api/document-ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: enhanced ?? result.text,
          action: aiAction,
          targetLanguage: aiAction === "translate" ? targetLang : undefined,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Enhancement failed");
      setEnhanced(data.enhanced);
      setStage("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unknown error");
      setStage("done");
    }
  };

  // ── Download ────────────────────────────────────────────────────────────────

  const isBinaryFormat = (fmt: string) => fmt === "docx" || fmt === "pdf";

  function downloadBinary(base64: string, mimeType: string, fileName: string) {
    const bytes = atob(base64);
    const arr = new Uint8Array(bytes.length);
    for (let i = 0; i < bytes.length; i++) arr[i] = bytes.charCodeAt(i);
    triggerDownload(new Blob([arr], { type: mimeType }), fileName);
  }

  const handleDownload = async (useEnhancedText = false) => {
    if (!result) return;
    const content = useEnhancedText && enhanced ? enhanced : null;

    if (content && isBinaryFormat(outputFormat)) {
      // Re-convert enhanced text through the API to generate a fresh binary file
      setStage("redownloading");
      setError("");
      try {
        const blob = new Blob([content], { type: "text/plain" });
        const enhFile = new File([blob], "enhanced.txt");
        const fd = new FormData();
        fd.append("file", enhFile);
        fd.append("outputFormat", outputFormat);
        const res = await fetch("/api/convert", { method: "POST", body: fd });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error ?? "Re-conversion failed");
        const baseName = result.fileName.replace(/\.[^.]+$/, "");
        downloadBinary(data.outputBase64, data.mimeType, `${baseName}-enhanced.${data.ext}`);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Download failed");
      } finally {
        setStage("done");
      }
    } else if (content) {
      // Text-based format: download enhanced text directly
      const textFormats: Record<string, string> = {
        md: "text/markdown", html: "text/html", txt: "text/plain",
        csv: "text/csv", json: "application/json", xml: "application/xml",
      };
      const mime = textFormats[outputFormat] ?? "text/plain";
      const textBlob = new Blob([content], { type: mime });
      triggerDownload(textBlob, `${result.fileName.replace(/\.[^.]+$/, "")}-enhanced.${outputFormat}`);
    } else {
      downloadBinary(result.outputBase64, result.mimeType, result.fileName);
    }
  };

  function triggerDownload(blob: Blob, name: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = name;
    a.click();
    URL.revokeObjectURL(url);
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  const converting    = stage === "converting";
  const enhancing     = stage === "enhancing";
  const redownloading = stage === "redownloading";
  const busy          = converting || enhancing || redownloading;

  const displayText = enhanced ?? result?.text ?? "";

  return (
    <div className="space-y-8 animate-fade-in">

      {/* Header */}
      <div className="space-y-2">
        <span className="text-label-sm uppercase tracking-[0.2em] text-secondary opacity-70">Universal Engine</span>
        <h2 className="font-serif text-headline-lg text-on-surface">Document Converter</h2>
        <p className="text-sm text-on-surface-variant/70">
          Convert between 15+ formats. AI-powered extraction, enhancement, and output.
        </p>
      </div>

      {/* Drop Zone — shown when idle */}
      {stage === "idle" && (
        <div
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => fileRef.current?.click()}
          className={cn(
            "flex flex-col items-center justify-center gap-6 p-16 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-300",
            dragging
              ? "border-primary bg-primary-container/10 scale-[1.005]"
              : "border-ink/50 dark:border-[#3d3a38] bg-surface-container-lowest dark:bg-[#25261f] hover:border-primary/50 hover:bg-surface-container-low/50",
            "paper-shadow",
          )}
        >
          <span className="material-symbols-outlined text-6xl text-on-surface-variant/30"
            style={{ fontVariationSettings: "'FILL' 0, 'wght' 200" }}>
            upload_file
          </span>
          <div className="text-center space-y-1">
            <p className="font-serif text-headline-md text-on-surface">Drop your document here</p>
            <p className="text-sm text-on-surface-variant/60">
              or <span className="text-primary dark:text-primary-fixed-dim underline underline-offset-2">click to browse</span>
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-1.5 max-w-lg">
            {FORMAT_BADGES.map(f => (
              <span key={f} className="text-[10px] px-2 py-0.5 rounded bg-surface-container dark:bg-[#232420] text-on-surface-variant/60 uppercase tracking-widest border border-ink/30 dark:border-[#3d3a38]">
                {f}
              </span>
            ))}
          </div>
          <p className="text-[11px] text-on-surface-variant/40">Max 15 MB</p>
          <input ref={fileRef} type="file" className="sr-only" accept={ACCEPTED} onChange={handleFileChange} />
        </div>
      )}

      {/* File card + options — shown when file is selected */}
      {stage !== "idle" && file && (
        <div className="space-y-6">
          {/* File info bar */}
          <div className="flex items-center justify-between bg-surface-container-low dark:bg-[#232420] border border-ink/30 dark:border-[#3d3a38] rounded-xl px-6 py-4">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 rounded-lg bg-primary-container/20 flex items-center justify-center">
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>description</span>
              </div>
              <div>
                <p className="font-sans text-sm font-medium text-on-surface truncate max-w-[280px]">{file.name}</p>
                <p className="text-[11px] text-on-surface-variant/60 uppercase tracking-widest mt-0.5">
                  {fileSizeLabel(file.size)} · {result?.inputLabel ?? "Detecting…"}
                  {result?.meta?.pages && ` · ${result.meta.pages} pages`}
                </p>
              </div>
            </div>
            <button
              onClick={reset}
              className="text-on-surface-variant/50 hover:text-primary transition-colors"
              title="Remove file"
            >
              <span className="material-symbols-outlined text-lg">close</span>
            </button>
          </div>

          <div className="grid lg:grid-cols-2 gap-6">
            {/* Output format */}
            <div className="space-y-3">
              <h3 className="text-label-sm uppercase tracking-[0.2em] text-on-surface-variant/60">Output Format</h3>
              <div className="flex flex-wrap gap-2">
                {OUTPUT_FORMATS.map(fmt => (
                  <button
                    key={fmt.id}
                    onClick={() => setOutput(fmt.id)}
                    disabled={busy}
                    className={cn(
                      "inline-flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium border transition-all",
                      outputFormat === fmt.id
                        ? "border-primary bg-primary-container text-on-primary"
                        : "border-ink dark:border-[#3d3a38] text-on-surface-variant hover:border-primary hover:text-primary dark:hover:border-primary-fixed-dim",
                      busy && "opacity-40 cursor-not-allowed",
                    )}
                  >
                    <span className="material-symbols-outlined text-[12px]">{fmt.icon}</span>
                    {fmt.label}
                  </button>
                ))}
              </div>
              {outputFormat === "pdf" && (
                <p className="text-[11px] text-on-surface-variant/50">
                  PDF output uses Helvetica. Non-ASCII characters are stripped. For rich formatting, use HTML then print to PDF.
                </p>
              )}
            </div>

            {/* AI Actions */}
            <div className="space-y-3">
              <h3 className="text-label-sm uppercase tracking-[0.2em] text-on-surface-variant/60">
                AI Enhancement <span className="font-normal normal-case opacity-60">— optional, runs after conversion</span>
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {AI_ACTIONS.map(action => (
                  <button
                    key={action.id}
                    onClick={() => setAiAction(aiAction === action.id ? null : action.id)}
                    disabled={busy}
                    className={cn(
                      "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all",
                      aiAction === action.id
                        ? "border-secondary bg-secondary-fixed text-on-secondary-container"
                        : "border-ink/50 dark:border-[#3d3a38] text-on-surface-variant hover:border-secondary/50",
                      busy && "opacity-40 cursor-not-allowed",
                    )}
                  >
                    <span className="material-symbols-outlined text-[11px]">{action.icon}</span>
                    {action.label}
                  </button>
                ))}
              </div>

              {aiAction === "translate" && (
                <div className="flex items-center gap-2">
                  <span className="text-[11px] text-on-surface-variant/60 uppercase tracking-widest">To:</span>
                  <input
                    value={targetLang}
                    onChange={e => setTargetLang(e.target.value)}
                    placeholder="Spanish"
                    className="bg-transparent border-b border-outline-variant/50 text-sm text-on-surface focus:border-primary outline-none px-1 py-0.5 w-32"
                  />
                </div>
              )}
            </div>
          </div>

          {/* Convert button */}
          {stage !== "done" && (
            <div className="flex justify-end">
              <button
                onClick={handleConvert}
                disabled={busy}
                className={cn(
                  "flex items-center gap-3 px-10 py-3.5 rounded-lg font-sans text-label-sm tracking-[0.2em] uppercase transition-all",
                  busy
                    ? "bg-surface-container text-on-surface-variant/40 cursor-not-allowed"
                    : "bg-primary-container text-on-primary hover:scale-[1.02] active:scale-95 shadow-sm hover:shadow-md",
                )}
              >
                {converting ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Converting…
                  </>
                ) : (
                  <>
                    Convert Document
                    <span className="material-symbols-outlined text-base">swap_horiz</span>
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="flex items-start gap-3 p-4 rounded-lg border border-error/30 bg-error-container/20 text-sm text-on-error-container">
          <span className="material-symbols-outlined text-error text-base mt-0.5">error</span>
          {error}
        </div>
      )}

      {/* Results */}
      {stage === "done" && result && (
        <div className="space-y-6 animate-fade-in">
          <div className="editorial-rule" />

          {/* Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <StatCard value={fmt(result.stats.inputWords)}  label="Input words" />
            <StatCard value={fmt(result.stats.outputWords)} label="Output words" />
            <StatCard value={fmt(displayText.length)}       label="Characters" />
            <StatCard
              value={outputFormat.toUpperCase()}
              label="Output format"
              delta={result.inputLabel}
              deltaGood={true}
            />
          </div>

          {/* Preview */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="font-serif text-headline-md text-on-surface">
                  {enhanced ? "Enhanced Document" : "Converted Document"}
                </h3>
                {enhanced && (
                  <span className="text-[11px] text-secondary uppercase tracking-widest">
                    AI · {AI_ACTIONS.find(a => a.id === aiAction)?.label}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-3">
                <CopyButton text={displayText} />
                <button
                  onClick={() => handleDownload(!!enhanced)}
                  disabled={redownloading}
                  className={cn(
                    "flex items-center gap-2 px-4 py-2 bg-primary-container text-on-primary text-label-sm uppercase tracking-widest rounded-lg transition-all text-xs",
                    redownloading ? "opacity-60 cursor-not-allowed" : "hover:opacity-90 active:scale-95",
                  )}
                >
                  {redownloading ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Generating…
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined text-sm">download</span>
                      Download {outputFormat.toUpperCase()}
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="vellum-surface dark:bg-[#232420] border border-ink dark:border-[#3d3a38] rounded-xl p-8 max-h-[480px] overflow-auto">
              <pre className="font-sans text-body-md text-on-surface leading-relaxed whitespace-pre-wrap break-words">
                {displayText}
              </pre>
            </div>
          </div>

          {/* Download original if enhanced */}
          {enhanced && (
            <div className="flex justify-end">
              <button
                onClick={() => handleDownload(false)}
                className="flex items-center gap-2 text-label-sm uppercase tracking-wider text-on-surface-variant/60 hover:text-primary transition-colors"
              >
                <span className="material-symbols-outlined text-sm">download</span>
                Download original conversion
              </button>
            </div>
          )}

          {/* AI Enhancement panel */}
          <div className="luxury-card rounded-xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="font-serif text-headline-md text-on-surface">AI Enhancement</h4>
                <p className="text-xs text-on-surface-variant/60 mt-0.5">
                  Apply an AI action to further transform the converted document
                </p>
              </div>
              {enhanced && (
                <button
                  onClick={() => setEnhanced(null)}
                  className="text-[11px] uppercase tracking-widest text-on-surface-variant/50 hover:text-primary transition-colors"
                >
                  Reset to original
                </button>
              )}
            </div>

            <div className="flex flex-wrap gap-1.5">
              {AI_ACTIONS.map(action => (
                <button
                  key={action.id}
                  onClick={() => setAiAction(aiAction === action.id ? null : action.id)}
                  disabled={enhancing}
                  className={cn(
                    "inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-medium border transition-all",
                    aiAction === action.id
                      ? "border-secondary bg-secondary-fixed text-on-secondary-container"
                      : "border-ink/50 dark:border-[#3d3a38] text-on-surface-variant hover:border-secondary/50",
                    enhancing && "opacity-40 cursor-not-allowed",
                  )}
                >
                  <span className="material-symbols-outlined text-[11px]">{action.icon}</span>
                  {action.label}
                </button>
              ))}
            </div>

            {aiAction === "translate" && (
              <div className="flex items-center gap-2">
                <span className="text-[11px] text-on-surface-variant/60 uppercase tracking-widest">To:</span>
                <input
                  value={targetLang}
                  onChange={e => setTargetLang(e.target.value)}
                  placeholder="Spanish"
                  className="bg-transparent border-b border-outline-variant/50 text-sm text-on-surface focus:border-primary outline-none px-1 py-0.5 w-32"
                />
              </div>
            )}

            <div className="flex justify-end">
              <button
                onClick={handleEnhance}
                disabled={!aiAction || enhancing}
                className={cn(
                  "flex items-center gap-2 px-6 py-2.5 rounded-lg font-sans text-label-sm tracking-[0.15em] uppercase transition-all",
                  !aiAction || enhancing
                    ? "bg-surface-container text-on-surface-variant/40 cursor-not-allowed"
                    : "bg-secondary-fixed text-on-secondary-container hover:scale-[1.02] active:scale-95 shadow-sm",
                )}
              >
                {enhancing ? (
                  <>
                    <span className="w-3 h-3 border-2 border-current/30 border-t-current rounded-full animate-spin" />
                    Enhancing…
                  </>
                ) : (
                  <>
                    <span className="material-symbols-outlined text-sm">auto_awesome</span>
                    Apply Enhancement
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Convert another */}
          <div className="flex justify-center pt-4">
            <button
              onClick={reset}
              className="flex items-center gap-2 text-label-sm uppercase tracking-wider text-on-surface-variant/50 hover:text-primary transition-colors"
            >
              <span className="material-symbols-outlined text-sm">add_circle</span>
              Convert another document
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
