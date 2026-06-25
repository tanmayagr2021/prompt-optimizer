"use client";

import { useState, useMemo } from "react";
import { TipCard } from "./tip-card";
import { cn } from "@/lib/utils";
import { getRandomTips, LEARN_CONTENT } from "@/lib/guidance";
import type { LearnItem } from "@/lib/types";

const CATEGORIES = Object.keys(LEARN_CONTENT);

function ArticleCard({ item }: { item: LearnItem }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={cn(
      "border rounded-xl transition-all duration-300",
      open
        ? "border-primary/30 dark:border-primary-fixed-dim/30 bg-primary-fixed/10"
        : "border-ink dark:border-[#3d3a38] luxury-card",
    )}>
      <button onClick={() => setOpen(!open)} className="w-full text-left px-6 py-5 flex items-start gap-4">
        <span className="text-2xl leading-none mt-0.5 shrink-0">{item.icon}</span>
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-1">
            <span className="font-serif text-base font-semibold text-on-surface">{item.title}</span>
            <span className={cn(
              "text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full",
              item.difficulty === "Beginner"     ? "bg-secondary-fixed text-on-secondary-fixed" :
              item.difficulty === "Intermediate"  ? "bg-primary-fixed text-on-primary-fixed-variant" :
              "bg-primary-container text-on-primary",
            )}>
              {item.difficulty}
            </span>
          </div>
          <span className="text-[10px] text-on-surface-variant/60 uppercase tracking-widest">{item.readTime} read</span>
          {!open && (
            <p className="text-sm text-on-surface-variant mt-1.5 leading-relaxed line-clamp-2">{item.summary}</p>
          )}
        </div>
        <span className={cn(
          "material-symbols-outlined text-on-surface-variant text-base mt-1 transition-transform duration-200 shrink-0",
          open && "rotate-180",
        )}>expand_more</span>
      </button>

      {open && (
        <div className="px-6 pb-6 space-y-5">
          <div className="editorial-rule" />
          <p className="text-sm text-on-surface-variant leading-relaxed">{item.summary}</p>
          <div>
            <p className="text-label-sm uppercase tracking-widest text-primary dark:text-primary-fixed-dim mb-3">Key Takeaways</p>
            <ul className="space-y-2">
              {item.keyPoints.map((point, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-on-surface-variant">
                  <span className="text-primary dark:text-primary-fixed-dim font-bold mt-0.5 shrink-0">→</span>
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
  const tips = useMemo(() => getRandomTips(3), []);
  const articles = LEARN_CONTENT[activeCategory] ?? [];

  return (
    <div className="space-y-10 animate-fade-in">
      {/* Header */}
      <div className="space-y-2">
        <span className="text-label-sm uppercase tracking-[0.2em] text-secondary opacity-70">The Art of the Instruction</span>
        <h2 className="font-serif text-headline-lg text-on-surface">Prompt Engineering Academy</h2>
        <p className="text-sm text-on-surface-variant">
          {CATEGORIES.length} categories · {Object.values(LEARN_CONTENT).flat().length}+ articles
        </p>
      </div>

      {/* Category pills */}
      <div className="flex flex-wrap gap-2">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={cn(
              "px-4 py-1.5 rounded-full text-label-sm uppercase tracking-wider transition-all",
              activeCategory === cat
                ? "bg-primary-container text-on-primary"
                : "border border-ink dark:border-[#3d3a38] text-on-surface-variant hover:border-primary hover:text-primary dark:hover:border-primary-fixed-dim",
            )}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Articles */}
      <div className="space-y-3">
        {articles.map((item) => <ArticleCard key={item.title} item={item} />)}
      </div>

      {/* Tips */}
      <div>
        <h3 className="font-serif text-headline-md text-on-surface mb-5">Quick Tips</h3>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {tips.map((tip) => <TipCard key={tip.id} tip={tip} />)}
        </div>
      </div>
    </div>
  );
}
