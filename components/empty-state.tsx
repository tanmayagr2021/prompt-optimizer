import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon: string;
  title: string;
  body: string;
  className?: string;
}

export function EmptyState({ icon, title, body, className }: EmptyStateProps) {
  return (
    <div className={cn(
      "rounded-xl border-2 border-dashed border-gray-200 dark:border-gray-800",
      "bg-gray-50/50 dark:bg-gray-900/30 p-10 text-center",
      className,
    )}>
      <div className="text-4xl mb-3">{icon}</div>
      <div className="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">{title}</div>
      <p className="text-xs text-gray-500 dark:text-gray-400 leading-relaxed max-w-xs mx-auto">{body}</p>
    </div>
  );
}
