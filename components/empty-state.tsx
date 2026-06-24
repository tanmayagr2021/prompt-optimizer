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
      "border border-dashed border-ink dark:border-[#3d3a38] rounded-xl",
      "vellum-surface p-10 text-center",
      className,
    )}>
      <div className="text-4xl mb-4">{icon}</div>
      <p className="font-serif text-sm font-semibold text-on-surface mb-2">{title}</p>
      <p className="text-xs text-on-surface-variant leading-relaxed max-w-xs mx-auto">{body}</p>
    </div>
  );
}
