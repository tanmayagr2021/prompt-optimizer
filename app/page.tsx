"use client";

import { cn } from "@/lib/utils";
import { OptimizerTab } from "@/components/optimizer-tab";
import { ArchitectTab } from "@/components/architect-tab";
import { LearnTab } from "@/components/learn-tab";
import { ConvertTab } from "@/components/convert-tab";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";
import { useTab } from "@/lib/tab-context";

const TABS = [
  { id: "optimizer",  label: "Workbench",  icon: "bolt" },
  { id: "architect",  label: "Architect",  icon: "architecture" },
  { id: "converter",  label: "Converter",  icon: "swap_horiz" },
  { id: "learn",      label: "Library",    icon: "history_edu" },
] as const;

type TabId = typeof TABS[number]["id"];

export default function Home() {
  const { activeTab, setActiveTab } = useTab();

  return (
    <div className="min-h-screen bg-background antialiased">
      <Header />

      <main className="max-w-[1280px] mx-auto px-5 md:px-16 py-16">
        {/* Hero */}
        <div className="text-center mb-16 space-y-6">
          <span className="text-label-sm uppercase tracking-[0.2em] text-secondary opacity-70">
            The Art of the Instruction
          </span>
          <h1 className="font-serif text-display-mob md:text-display-lg text-on-surface tracking-tighter leading-tight">
            Craft Better Prompts.
          </h1>
          <p className="text-body-lg text-on-surface-variant max-w-2xl mx-auto leading-relaxed opacity-80">
            Turn rough ideas into beautifully engineered instructions. Precision, prestige, and power for the modern creative technologist.
          </p>
          <div className="editorial-rule max-w-xs mx-auto" />
        </div>

        {/* Tabs — editorial navigation */}
        <div className="flex border-b border-ink dark:border-[#3d3a38] mb-12 gap-0">
          {TABS.map(({ id, label, icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id as TabId)}
              className={cn(
                "relative flex items-center gap-2 px-6 py-4 font-sans text-sm font-medium transition-colors",
                activeTab === id
                  ? "text-primary dark:text-primary-fixed-dim"
                  : "text-on-surface-variant/70 hover:text-on-surface",
              )}
            >
              <span className="material-symbols-outlined text-base">{icon}</span>
              {label}
              {activeTab === id && (
                <span className="absolute bottom-0 left-0 right-0 h-px bg-primary dark:bg-primary-fixed-dim" />
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === "optimizer"  && <OptimizerTab />}
        {activeTab === "architect"  && <ArchitectTab />}
        {activeTab === "converter"  && <ConvertTab />}
        {activeTab === "learn"      && <LearnTab />}
      </main>

      <Footer />
    </div>
  );
}
