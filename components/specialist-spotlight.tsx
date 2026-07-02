"use client";

import { useEffect, useState } from "react";
import { useTab } from "@/lib/tab-context";

const DISMISS_KEY = "sp-specialist-spotlight-dismissed";

export function SpecialistSpotlight() {
  const { setActiveTab } = useTab();
  const [dismissed, setDismissed] = useState(true);

  useEffect(() => {
    setDismissed(localStorage.getItem(DISMISS_KEY) === "1");
  }, []);

  const dismiss = () => {
    localStorage.setItem(DISMISS_KEY, "1");
    setDismissed(true);
  };

  if (dismissed) return null;

  return (
    <div className="luxury-card rounded-xl p-6 md:p-8 relative overflow-hidden animate-fade-in">
      <button
        onClick={dismiss}
        aria-label="Dismiss"
        className="absolute top-4 right-4 text-on-surface-variant/40 hover:text-primary transition-colors"
      >
        <span className="material-symbols-outlined text-lg">close</span>
      </button>

      <span className="inline-flex items-center gap-1.5 text-label-sm uppercase tracking-widest px-2.5 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed mb-4 font-sans">
        <span className="material-symbols-outlined text-sm">auto_awesome</span>
        Your Prompt Specialist
      </span>

      <h3 className="font-serif text-headline-md md:text-headline-lg text-on-surface mb-3 max-w-2xl">
        Two ways to get a perfect prompt.
      </h3>

      <div className="grid sm:grid-cols-2 gap-5 mb-6 max-w-2xl">
        <div className="flex gap-3">
          <span className="material-symbols-outlined text-primary dark:text-primary-fixed-dim mt-0.5 shrink-0">bolt</span>
          <div>
            <p className="text-sm font-semibold text-on-surface">Have a rough prompt?</p>
            <p className="text-sm text-on-surface-variant leading-relaxed">
              Paste it in the Workbench below and we&apos;ll engineer &amp; optimise it for clarity and precision.
            </p>
          </div>
        </div>
        <div className="flex gap-3">
          <span className="material-symbols-outlined text-primary dark:text-primary-fixed-dim mt-0.5 shrink-0">architecture</span>
          <div>
            <p className="text-sm font-semibold text-on-surface">Only have a brief idea?</p>
            <p className="text-sm text-on-surface-variant leading-relaxed">
              Just describe your goal in a sentence — we&apos;ll write the full, production-ready prompt for you.
            </p>
          </div>
        </div>
      </div>

      <button
        onClick={() => setActiveTab("architect")}
        className="inline-flex items-center gap-2 px-6 py-3 rounded-lg bg-primary-container text-on-primary font-sans text-label-sm tracking-widest uppercase hover:opacity-90 active:scale-95 transition-all"
      >
        Give me a brief idea
        <span className="material-symbols-outlined text-base">arrow_forward</span>
      </button>
    </div>
  );
}
