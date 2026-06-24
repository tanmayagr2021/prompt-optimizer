import { ThemeToggle } from "./theme-toggle";

export function Header() {
  return (
    <header className="sticky top-0 z-50 bg-surface/80 dark:bg-[#1b1c19]/80 backdrop-blur-md border-b border-outline-variant/30 transition-all duration-300">
      <div className="flex justify-between items-center w-full px-5 md:px-16 py-5 max-w-[1280px] mx-auto">
        <div className="font-serif text-headline-lg font-semibold text-primary dark:text-primary-fixed-dim tracking-tighter">
          StingyPocketEngineer
        </div>

        <nav className="hidden md:flex items-center gap-10">
          <a className="text-primary dark:text-primary-fixed-dim font-semibold border-b border-primary dark:border-primary-fixed-dim pb-0.5 font-sans text-sm">
            Workbench
          </a>
          <a className="text-on-surface-variant/70 font-medium hover:text-primary dark:hover:text-primary-fixed-dim transition-colors duration-300 font-sans text-sm cursor-pointer">
            Library
          </a>
          <a className="text-on-surface-variant/70 font-medium hover:text-primary dark:hover:text-primary-fixed-dim transition-colors duration-300 font-sans text-sm cursor-pointer">
            Models
          </a>
          <a className="text-on-surface-variant/70 font-medium hover:text-primary dark:hover:text-primary-fixed-dim transition-colors duration-300 font-sans text-sm cursor-pointer">
            Archive
          </a>
        </nav>

        <div className="flex items-center gap-4">
          <ThemeToggle />
          <button className="bg-primary-container text-on-primary px-5 py-2 rounded-lg font-sans text-label-sm tracking-widest uppercase hover:opacity-90 active:scale-95 transition-all text-xs">
            New Prompt
          </button>
        </div>
      </div>
    </header>
  );
}
