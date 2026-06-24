"use client";

import { useTheme } from "next-themes";
import { useEffect, useState } from "react";

export function ThemeToggle({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => { setMounted(true); }, []);

  if (!mounted) return <div className="w-10 h-10 rounded-full border border-ink animate-pulse" />;

  const isDark = resolvedTheme === "dark";

  return (
    <button
      onClick={() => setTheme(isDark ? "light" : "dark")}
      aria-label={isDark ? "Switch to light mode" : "Switch to dark mode"}
      className={`w-10 h-10 rounded-full border border-ink dark:border-[#3d3a38] flex items-center justify-center text-on-surface-variant hover:text-primary hover:border-primary dark:hover:border-primary-fixed-dim transition-all ${className ?? ""}`}
    >
      <span className="material-symbols-outlined text-sm">{isDark ? "light_mode" : "dark_mode"}</span>
    </button>
  );
}
