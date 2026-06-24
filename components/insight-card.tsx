import { cn } from "@/lib/utils";
import type { Insight } from "@/lib/types";

export function InsightCard({ insight }: { insight: Insight }) {
  return (
    <div className="bg-surface-container-low dark:bg-[#232420] border border-outline-variant/30 rounded-lg p-6 hover:shadow-card transition-shadow group">
      <div className="flex items-center gap-2 mb-4">
        <span className="material-symbols-outlined text-primary dark:text-primary-fixed-dim text-base"
          style={{ fontVariationSettings: "'FILL' 1" }}>
          {iconFor(insight.category)}
        </span>
        <span className="text-label-sm uppercase tracking-widest text-on-surface">{insight.category}</span>
      </div>
      <p className="text-sm font-semibold text-on-surface mb-1">{insight.change}</p>
      <p className="text-xs text-on-surface-variant leading-relaxed">{insight.why}</p>
    </div>
  );
}

function iconFor(category: string): string {
  const map: Record<string, string> = {
    Structure: "account_tree", Clarity: "clarity", Constraints: "rule",
    Format: "format_list_bulleted", Role: "person", Efficiency: "bolt",
    Specificity: "adjust",
  };
  return map[category] ?? "auto_fix";
}
