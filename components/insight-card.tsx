import { cn } from "@/lib/utils";
import type { Insight } from "@/lib/types";

const BORDER_COLORS: Record<string, string> = {
  indigo:  "border-l-indigo-500",
  blue:    "border-l-blue-500",
  green:   "border-l-emerald-500",
  purple:  "border-l-purple-500",
  orange:  "border-l-orange-500",
  yellow:  "border-l-yellow-500",
  teal:    "border-l-teal-500",
};

const CAT_COLORS: Record<string, string> = {
  indigo:  "text-indigo-600 dark:text-indigo-400",
  blue:    "text-blue-600 dark:text-blue-400",
  green:   "text-emerald-600 dark:text-emerald-400",
  purple:  "text-purple-600 dark:text-purple-400",
  orange:  "text-orange-600 dark:text-orange-400",
  yellow:  "text-yellow-600 dark:text-yellow-400",
  teal:    "text-teal-600 dark:text-teal-400",
};

export function InsightCard({ insight }: { insight: Insight }) {
  const borderCls = BORDER_COLORS[insight.color] ?? BORDER_COLORS.indigo;
  const catCls    = CAT_COLORS[insight.color]    ?? CAT_COLORS.indigo;
  return (
    <div className={cn(
      "border-l-[3px] border border-gray-100 dark:border-gray-800/60 rounded-r-lg",
      "bg-gray-50 dark:bg-gray-900/50 p-3 transition-transform hover:translate-x-0.5",
      borderCls,
    )}>
      <div className={cn("text-[0.62rem] font-bold uppercase tracking-widest mb-1", catCls)}>
        {insight.icon} {insight.category}
      </div>
      <div className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-0.5">{insight.change}</div>
      <div className="text-[0.77rem] text-gray-500 dark:text-gray-400 leading-snug">{insight.why}</div>
    </div>
  );
}
