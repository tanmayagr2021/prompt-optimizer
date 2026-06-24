import { ThemeToggle } from "./theme-toggle";
import { Zap } from "lucide-react";

export function Header() {
  return (
    <header className="sticky top-0 z-30 w-full border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center shadow-sm">
            <Zap size={16} className="text-white" />
          </div>
          <div>
            <span className="text-sm font-bold text-gray-900 dark:text-gray-100 tracking-tight">
              PromptCraft
            </span>
            <span className="hidden sm:inline text-xs text-gray-400 dark:text-gray-500 ml-2">
              AI Prompt Optimizer
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="https://console.groq.com"
            target="_blank"
            rel="noreferrer"
            className="hidden sm:inline-flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            Powered by Groq
          </a>
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
