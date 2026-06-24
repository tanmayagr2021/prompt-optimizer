import { cn } from "@/lib/utils";
import type { Tip } from "@/lib/types";

const TYPE_COLORS: Record<string, string> = {
  "Pro Tip":      "bg-indigo-50 dark:bg-indigo-950/40 border-indigo-200 dark:border-indigo-800",
  "Best Practice":"bg-emerald-50 dark:bg-emerald-950/40 border-emerald-200 dark:border-emerald-800",
  "Did You Know": "bg-sky-50 dark:bg-sky-950/40 border-sky-200 dark:border-sky-800",
  "Workflow":     "bg-amber-50 dark:bg-amber-950/40 border-amber-200 dark:border-amber-800",
  "Insight":      "bg-violet-50 dark:bg-violet-950/40 border-violet-200 dark:border-violet-800",
};

const TAG_COLORS: Record<string, string> = {
  "Pro Tip":      "text-indigo-600 dark:text-indigo-400 bg-indigo-100 dark:bg-indigo-900/50",
  "Best Practice":"text-emerald-600 dark:text-emerald-400 bg-emerald-100 dark:bg-emerald-900/50",
  "Did You Know": "text-sky-600 dark:text-sky-400 bg-sky-100 dark:bg-sky-900/50",
  "Workflow":     "text-amber-600 dark:text-amber-400 bg-amber-100 dark:bg-amber-900/50",
  "Insight":      "text-violet-600 dark:text-violet-400 bg-violet-100 dark:bg-violet-900/50",
};

const TITLE_COLORS: Record<string, string> = {
  "Pro Tip":      "text-indigo-900 dark:text-indigo-100",
  "Best Practice":"text-emerald-900 dark:text-emerald-100",
  "Did You Know": "text-sky-900 dark:text-sky-100",
  "Workflow":     "text-amber-900 dark:text-amber-100",
  "Insight":      "text-violet-900 dark:text-violet-100",
};

const BODY_COLORS: Record<string, string> = {
  "Pro Tip":      "text-indigo-700 dark:text-indigo-300",
  "Best Practice":"text-emerald-700 dark:text-emerald-300",
  "Did You Know": "text-sky-700 dark:text-sky-300",
  "Workflow":     "text-amber-700 dark:text-amber-300",
  "Insight":      "text-violet-700 dark:text-violet-300",
};

interface TipCardProps {
  tip: Tip;
  className?: string;
}

export function TipCard({ tip, className }: TipCardProps) {
  const cardCls   = TYPE_COLORS[tip.type]   ?? TYPE_COLORS["Insight"];
  const tagCls    = TAG_COLORS[tip.type]    ?? TAG_COLORS["Insight"];
  const titleCls  = TITLE_COLORS[tip.type]  ?? TITLE_COLORS["Insight"];
  const bodyCls   = BODY_COLORS[tip.type]   ?? BODY_COLORS["Insight"];

  return (
    <div className={cn("rounded-xl border p-4 transition-all hover:-translate-y-0.5 hover:shadow-md", cardCls, className)}>
      <span className={cn("inline-block text-[0.65rem] font-bold uppercase tracking-widest px-2 py-0.5 rounded-full mb-2", tagCls)}>
        {tip.icon} {tip.type}
      </span>
      <p className={cn("text-sm font-semibold mb-1", titleCls)}>{tip.title}</p>
      <p className={cn("text-[0.8rem] leading-relaxed", bodyCls)}>{tip.body}</p>
    </div>
  );
}
