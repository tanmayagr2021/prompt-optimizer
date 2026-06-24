"use client";

import { useState } from "react";
import { BookOpen, ChevronDown, Clock } from "lucide-react";
import { TipCard } from "./tip-card";
import { cn } from "@/lib/utils";
import { getRandomTips } from "@/lib/guidance";
import { LEARN_CONTENT } from "@/lib/guidance";
import type { LearnItem } from "@/lib/types";

const CATEGORIES = Object.keys(LEARN_CONTENT);

const DIFFICULTY_COLORS: Record<string, string> = {
  Beginner:     "bg-emerald-100 dark:bg-emerald-900/50 text-emerald-700 dark:text-emerald-300",
  Intermediate: "bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300",
  Advanced:     "bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300",
};

function ArticleCard({ item }: { item: LearnItem }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={cn(
      "rounded-xl border transition-all duration-200",
      open
        ? "border-indigo-200 dark:border-indigo-800 bg-indigo-50/30 dark:bg-indigo-950/20"
        : "border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900/50 hover:border-gray-300 dark:hover:border-gray-700",
    )}>
      <button
        onClick={() => setOpen(!open)}
        className="w-full text-left px-5 py-4 flex items-start gap-3"
      >
        <span className="text-2xl leading-none mt-0.5 shrink-0">{item.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="text-sm font-semibold text-gray-800 dark:text-gray-200">{item.title}</span>
            <span className={cn("text-[0.6rem] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded-full", DIFFICULTY_COLORS[item.difficulty] ?? DIFFICULTY_COLORS.Beginner)}>
              {item.difficulty}
            </span>
          </div>
          <div className="flex items-center gap-1 text-[0.7rem] text-gray-400 dark:text-gray-500">
            <Clock size={10} />
            {item.readTime} read
          </div>
          {!open && (
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1.5 leading-relaxed line-clamp-2">
              {item.summary}
            </p>
          )}
        </div>
        <ChevronDown
          size={15}
          className={cn(
            "shrink-0 text-gray-400 transition-transform duration-200 mt-1",
            open && "rotate-180",
          )}
        />
      </button>

      {open && (
        <div className="px-5 pb-5 space-y-4">
          <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{item.summary}</p>
          <div>
            <p className="text-[0.7rem] font-bold uppercase tracking-widest text-indigo-600 dark:text-indigo-400 mb-2">
              Key Takeaways
            </p>
            <ul className="space-y-1.5">
              {item.keyPoints.map((point, i) => (
                <li key={i} className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-300">
                  <span className="text-indigo-500 dark:text-indigo-400 font-bold shrink-0 mt-0.5">→</span>
                  {point}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export function LearnTab() {
  const [activeCategory, setActiveCategory] = useState(CATEGORIES[0]);
  const tips = getRandomTips(3);
  const articles = LEARN_CONTENT[activeCategory] ?? [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start gap-3">
        <div className="w-10 h-10 rounded-xl bg-violet-100 dark:bg-violet-900/40 flex items-center justify-center shrink-0">
          <BookOpen size={18} className="text-violet-600 dark:text-violet-400" />
        </div>
        <div>
          <h2 className="text-base font-bold text-gray-900 dark:text-gray-100">Prompt Engineering Academy</h2>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            {CATEGORIES.length} categories · {Object.values(LEARN_CONTENT).flat().length}+ articles
          </p>
        </div>
      </div>

      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={cn(
              "px-3 py-1.5 rounded-full text-xs font-semibold transition-all",
              activeCategory === cat
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700",
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles */}
      <div className="space-y-3">
        {articles.map((item) => (
          <ArticleCard key={item.title} item={item} />
        ))}
      </div>

      {/* Tips section */}
      <div>
        <h3 className="text-sm font-bold text-gray-700 dark:text-gray-300 mb-3">Quick Tips</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {tips.map((tip) => (
            <TipCard key={tip.id} tip={tip} />
          ))}
        </div>
      </div>
    </div>
  );
}
