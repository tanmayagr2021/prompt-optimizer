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
    <div className={cn(
      "rounded-xl border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50",
      "p-3.5 text-center transition-all hover:-translate-y-0.5 hover:shadow-md",
      className,
    )}>
      <div className="text-xl font-extrabold tracking-tight text-gray-900 dark:text-gray-100">
        {value}
      </div>
      {delta && (
        <div className={cn("text-xs font-semibold mt-0.5", deltaGood ? "text-emerald-600 dark:text-emerald-400" : "text-gray-400")}>
          {delta}
        </div>
      )}
      <div className="text-[0.68rem] text-gray-500 dark:text-gray-400 mt-1">{label}</div>
    </div>
  );
}
