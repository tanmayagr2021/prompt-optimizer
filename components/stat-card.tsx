import { cn } from "@/lib/utils";

interface StatCardProps {
  value: string;
  label: string;
  delta?: string;
  deltaGood?: boolean;
  className?: string;
}

export function StatCard({ value, label, delta, deltaGood = true, className }: StatCardProps) {
  return (
    <div className={cn("luxury-card rounded-xl p-4 text-center", className)}>
      <div className="font-serif text-headline-md text-on-surface">{value}</div>
      {delta && (
        <div className={cn("text-xs font-semibold mt-0.5", deltaGood ? "text-secondary" : "text-on-surface-variant/60")}>
          {delta}
        </div>
      )}
      <div className="text-label-sm text-on-surface-variant/60 uppercase tracking-widest mt-1">{label}</div>
    </div>
  );
}
