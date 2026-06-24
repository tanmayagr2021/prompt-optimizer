"use client";

import { useState } from "react";
import { Zap, Building2, BookOpen } from "lucide-react";
import { cn } from "@/lib/utils";
import { OptimizerTab } from "@/components/optimizer-tab";
import { ArchitectTab } from "@/components/architect-tab";
import { LearnTab } from "@/components/learn-tab";
import { Header } from "@/components/header";
import { Footer } from "@/components/footer";

const TABS = [
  { id: "optimizer", label: "Optimizer",  icon: Zap,       shortLabel: "Optimize" },
  { id: "architect", label: "Architect",  icon: Building2, shortLabel: "Architect" },
  { id: "learn",     label: "Learn",      icon: BookOpen,  shortLabel: "Learn" },
] as const;

type TabId = typeof TABS[number]["id"];

export default function Home() {
  const [activeTab, setActiveTab] = useState<TabId>("optimizer");

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 antialiased">
      <Header />

      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-8">
        {/* Hero */}
        <div className="text-center mb-10">
          <div className="inline-flex items-center gap-2 bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-200 dark:border-indigo-800 rounded-full px-4 py-1.5 mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
            <span className="text-xs font-semibold text-indigo-600 dark:text-indigo-400">
              Powered by Groq LLaMA 3.3 70B
            </span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100 mb-3">
            PromptCraft
          </h1>
          <p className="text-gray-500 dark:text-gray-400 text-sm sm:text-base max-w-xl mx-auto leading-relaxed">
            Transform rough prompts into precision-engineered instructions.
            Architect platform-specific prompts from scratch. Learn from 30+ expert techniques.
          </p>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-800 mb-8 gap-1">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={cn(
                "relative flex items-center gap-2 px-4 py-3 text-sm font-semibold transition-colors",
                "focus:outline-none",
                activeTab === id
                  ? "text-indigo-600 dark:text-indigo-400"
                  : "text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200",
              )}
            >
              <Icon size={15} />
              <span className="hidden sm:inline">{label}</span>
              <span className="sm:hidden">{label}</span>
              {activeTab === id && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-indigo-600 dark:bg-indigo-400 rounded-full" />
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div>
          {activeTab === "optimizer" && <OptimizerTab />}
          {activeTab === "architect" && <ArchitectTab />}
          {activeTab === "learn"     && <LearnTab />}
        </div>
      </main>

      <Footer />
    </div>
  );
}
