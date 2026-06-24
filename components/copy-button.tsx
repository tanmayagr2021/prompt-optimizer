"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

export function CopyButton({ text, className, label = "Copy" }: { text: string; className?: string; label?: string }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const el = document.createElement("textarea");
      el.value = text;
      el.style.cssText = "position:fixed;opacity:0";
      document.body.appendChild(el);
      el.select();
      document.execCommand("copy");
      document.body.removeChild(el);
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <button
      onClick={handleCopy}
      className={cn(
        "inline-flex items-center gap-1.5 font-sans text-label-sm uppercase tracking-wider px-3 py-1.5 rounded transition-all",
        copied
          ? "bg-secondary-fixed text-on-secondary-fixed"
          : "border border-ink dark:border-[#3d3a38] text-on-surface-variant hover:text-primary hover:border-primary dark:hover:border-primary-fixed-dim",
        className,
      )}
    >
      <span className="material-symbols-outlined text-xs">{copied ? "check" : "content_copy"}</span>
      {copied ? "Copied!" : label}
    </button>
  );
}
