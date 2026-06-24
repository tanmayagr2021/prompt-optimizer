export function Footer() {
  return (
    <footer className="mt-16 border-t border-gray-200 dark:border-gray-800 py-8">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-3">
        <p className="text-xs text-gray-400 dark:text-gray-500">
          Built with Next.js &amp; Groq
        </p>
        <a
          href="mailto:tanmayagr2021@gmail.com"
          className="text-xs text-gray-400 dark:text-gray-500 hover:text-indigo-600 dark:hover:text-indigo-400 transition-colors"
        >
          tanmayagr2021@gmail.com
        </a>
      </div>
    </footer>
  );
}
