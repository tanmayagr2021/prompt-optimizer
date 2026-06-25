"use client";

import { ThemeToggle } from "./theme-toggle";
import { cn } from "@/lib/utils";
import { useTab } from "@/lib/tab-context";
import type { TabId } from "@/lib/tab-context";

const NAV: { id: TabId; label: string }[] = [
  { id: "optimizer", label: "Workbench" },
  { id: "architect", label: "Architect" },
  { id: "learn",     label: "Library"   },
];

export function Header() {
  const { activeTab, setActiveTab } = useTab();

  return (
    <header className="sticky top-0 z-50 bg-surface/80 dark:bg-[#1b1c19]/80 backdrop-blur-md border-b border-outline-variant/30 transition-all duration-300">
      <div className="flex justify-between items-center w-full px-5 md:px-16 py-5 max-w-[1280px] mx-auto">
        <button
          onClick={() => setActiveTab("optimizer")}
          className="font-serif text-headline-lg font-semibold text-primary dark:text-primary-fixed-dim tracking-tighter hover:opacity-80 transition-opacity"
        >
          StingyPocketEngineer
        </button>

        <nav className="hidden md:flex items-center gap-10">
          {NAV.map(({ id, label }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={cn(
                "font-sans text-sm transition-colors duration-200",
                activeTab === id
                  ? "text-primary dark:text-primary-fixed-dim font-semibold border-b border-primary dark:border-primary-fixed-dim pb-0.5"
                  : "text-on-surface-variant/70 font-medium hover:text-primary dark:hover:text-primary-fixed-dim",
              )}
            >
              {label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <button
            onClick={() => {
              setActiveTab("optimizer");
              window.scrollTo({ top: 0, behavior: "smooth" });
            }}
            className="bg-primary-container text-on-primary px-5 py-2 rounded-lg font-sans text-label-sm tracking-widest uppercase hover:opacity-90 active:scale-95 transition-all text-xs"
          >
            New Prompt
          </button>
        </div>
      </div>
    </header>
  );
}
