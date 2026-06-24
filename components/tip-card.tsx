import { cn } from "@/lib/utils";
import type { Tip } from "@/lib/types";

export function TipCard({ tip, className }: { tip: Tip; className?: string }) {
  return (
    <div className={cn("luxury-card rounded-xl p-5", className)}>
      <span className="inline-block text-label-sm uppercase tracking-widest px-2.5 py-1 rounded-full bg-secondary-fixed text-on-secondary-fixed mb-3 font-sans">
        {tip.icon} {tip.type}
      </span>
      <p className="font-serif text-base font-semibold text-on-surface mb-1.5 leading-snug">{tip.title}</p>
      <p className="text-sm text-on-surface-variant leading-relaxed">{tip.body}</p>
    </div>
  );
}
