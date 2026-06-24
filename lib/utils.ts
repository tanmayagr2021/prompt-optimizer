import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function fmt(n: number): string {
  return n.toLocaleString();
}

export function estimateTokens(text: string): number {
  return Math.max(1, Math.floor(text.length / 4));
}

export function calcStats(original: string, optimized: string) {
  const origChars = original.length;
  const optChars  = optimized.length;
  const removed   = origChars - optChars;
  const reductPct = origChars > 0 ? (removed / origChars) * 100 : 0;
  const origTok   = estimateTokens(original);
  const optTok    = estimateTokens(optimized);
  const tokRemoved = origTok - optTok;
  const tokPct    = origTok > 0 ? (tokRemoved / origTok) * 100 : 0;
  return { origChars, optChars, removed, reductPct, origTok, optTok, tokRemoved, tokPct };
}
