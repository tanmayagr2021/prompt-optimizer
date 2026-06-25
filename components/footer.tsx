export function Footer() {
  return (
    <footer className="bg-surface-container-low dark:bg-[#232420] border-t border-outline-variant/20 mt-20">
      <div className="flex flex-col md:flex-row justify-between items-center w-full px-5 md:px-16 py-16 max-w-[1280px] mx-auto gap-10 md:gap-0">
        <div className="text-center md:text-left space-y-3">
          <div className="font-serif text-headline-md text-on-surface">
            StingyPocketEngineer
          </div>
          <p className="text-sm text-tertiary opacity-70">
            © 2025 StingyPocketEngineer. Crafted for the discerning technologist.
          </p>
          <a
            href="mailto:tanmayagr2021@gmail.com"
            className="text-xs text-on-surface-variant hover:text-primary dark:hover:text-primary-fixed-dim transition-colors"
          >
            tanmayagr2021@gmail.com
          </a>
        </div>

        <div className="flex gap-12">
          <div className="flex flex-col gap-3">
            <span className="text-label-sm text-on-surface-variant/40 uppercase tracking-[0.2em] mb-1">Platform</span>
            <a className="text-sm text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Philosophy</a>
            <a className="text-sm text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Journal</a>
          </div>
          <div className="flex flex-col gap-3">
            <span className="text-label-sm text-on-surface-variant/40 uppercase tracking-[0.2em] mb-1">Legal</span>
            <a className="text-sm text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Privacy</a>
            <a className="text-sm text-on-surface-variant hover:text-primary transition-colors cursor-pointer">Terms</a>
          </div>
        </div>

        <div className="flex gap-4">
          <div className="w-10 h-10 border border-ink dark:border-[#3d3a38] rounded-full flex items-center justify-center hover:bg-on-surface hover:text-surface transition-all cursor-pointer">
            <span className="material-symbols-outlined text-sm">terminal</span>
          </div>
          <div className="w-10 h-10 border border-ink dark:border-[#3d3a38] rounded-full flex items-center justify-center hover:bg-on-surface hover:text-surface transition-all cursor-pointer">
            <span className="material-symbols-outlined text-sm">history_edu</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
