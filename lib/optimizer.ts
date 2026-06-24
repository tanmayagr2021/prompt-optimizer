// Rule-based 6-pass prompt optimizer (TypeScript port)

const FILLER_PHRASES = [
  /\b(please|kindly)\b\s*/gi,
  /\bi\s+would\s+like\s+(you\s+to\s+)?/gi,
  /\bi\s+want\s+you\s+to\s+/gi,
  /\bcould\s+you\s+(please\s+)?/gi,
  /\bcan\s+you\s+(please\s+)?/gi,
  /\bwould\s+you\s+mind\s+/gi,
  /\bi\s+think\s+/gi,
  /\bmaybe\s+/gi,
  /\bperhaps\s+/gi,
  /\bi\s+believe\s+/gi,
  /\bsort\s+of\s+/gi,
  /\bbasically\s+/gi,
  /\bactually\s+/gi,
  /\bjust\s+/gi,
  /\bsimply\s+/gi,
  /\bvery\s+/gi,
  /\breally\s+/gi,
  /\bquite\s+/gi,
  /\bextremely\s+/gi,
  /\bit\s+is\s+important\s+to\s+note\s+that\s+/gi,
  /\bplease\s+note\s+that\s+/gi,
  /\bas\s+mentioned\s+(above|earlier|before)\s+/gi,
  /\bfor\s+context[,:]?\s+/gi,
  /^(Also|Additionally|Furthermore|Moreover|On\s+top\s+of\s+that)[,:]?\s+/gim,
  /\bif\s+you\s+can\b/gi,
  /\bit\s+would\s+be\s+nice\s+if\b/gi,
  /\bwhenever\s+possible\b/gi,
  /\bfeel\s+free\s+to\b/gi,
];

const COMPRESSIONS: [RegExp, string][] = [
  [/\bin\s+order\s+to\b/gi, "to"],
  [/\bmake\s+use\s+of\b/gi, "use"],
  [/\bhas\s+the\s+ability\s+to\b/gi, "can"],
  [/\bmake\s+sure\s+to\s+/gi, ""],
  [/\bin\s+the\s+event\s+that\b/gi, "if"],
  [/\ba\s+large\s+number\s+of\b/gi, "many"],
  [/\bat\s+this\s+point\s+in\s+time\b/gi, "currently"],
  [/\bdue\s+to\s+the\s+fact\s+that\b/gi, "because"],
  [/\bprior\s+to\b/gi, "before"],
  [/\bsubsequent\s+to\b/gi, "after"],
  [/\bwith\s+regard\s+to\b/gi, "regarding"],
  [/\bin\s+spite\s+of\s+the\s+fact\s+that\b/gi, "although"],
];

function normalizeWhitespace(text: string): string {
  return text
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n")
    .replace(/[ \t]+/g, " ")
    .replace(/[ \t]+\n/g, "\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

function removeFiller(text: string): string {
  let result = text;
  for (const pattern of FILLER_PHRASES) {
    result = result.replace(pattern, "");
  }
  return result;
}

function compress(text: string): string {
  let result = text;
  for (const [from, to] of COMPRESSIONS) {
    result = result.replace(from, to);
  }
  return result;
}

function hasStructure(text: string): boolean {
  return /^#{1,3}\s/m.test(text) || /^[-*•]\s/m.test(text);
}

function hasRole(text: string): boolean {
  return /^(you are|act as|you're a|as a senior|as an expert)/i.test(text.trim().slice(0, 200));
}

function injectRole(text: string): string {
  // Only inject if no role exists and text is substantive
  if (hasRole(text) || text.length < 50) return text;
  const lower = text.toLowerCase();
  if (lower.includes("write") || lower.includes("create") || lower.includes("generate")) {
    return "You are an expert. " + text;
  }
  if (lower.includes("analyze") || lower.includes("review") || lower.includes("evaluate")) {
    return "You are a senior analyst. " + text;
  }
  if (lower.includes("explain") || lower.includes("describe") || lower.includes("summarize")) {
    return "You are a clear technical communicator. " + text;
  }
  return text;
}

function addOutputFormat(text: string): string {
  const lower = text.toLowerCase();
  const hasFormat = /\b(format|structure|output|respond|return)\b/i.test(text);
  if (hasFormat) return text;
  if (lower.includes("list") || lower.includes("bullet")) {
    return text + "\n\nFormat your response as a clear bulleted list.";
  }
  if (lower.includes("report") || lower.includes("analysis") || lower.includes("document")) {
    return text + "\n\nStructure your response with clear sections and headers.";
  }
  return text;
}

export interface RuleResult {
  optimized: string;
  mode: "small" | "medium" | "large";
}

export function ruleOptimize(input: string): RuleResult {
  let text = normalizeWhitespace(input);
  const originalLen = text.length;

  // Pass 1: remove filler
  text = removeFiller(text);
  // Pass 2: compress phrases
  text = compress(text);
  // Pass 3: inject role if missing
  text = injectRole(text);
  // Pass 4: add output format hint if missing
  text = addOutputFormat(text);
  // Pass 5: final normalize
  text = normalizeWhitespace(text);

  const ratio = text.length / originalLen;
  const mode: RuleResult["mode"] = ratio > 0.85 ? "large" : ratio > 0.65 ? "medium" : "small";

  return { optimized: text, mode };
}
