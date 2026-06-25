import type { NextConfig } from "next";

const config: NextConfig = {
  // These packages use native Node.js require() and must not be bundled by webpack.
  // Without this, Vercel's bundler breaks CJS/ESM interop for binary document libraries.
  serverExternalPackages: [
    "pdf-parse",
    "mammoth",
    "xlsx",
    "docx",
    "pdf-lib",
    "jszip",
    "turndown",
    "groq-sdk",
  ],
};

export default config;
