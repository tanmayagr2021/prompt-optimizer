import type { Insight } from "./types";

export function analyzeChanges(original: string, optimized: string): Insight[] {
  const insights: Insight[] = [];

  // Structure: headers added
  const origH = (original.match(/^#{1,3}\s/gm) ?? []).length;
  const optH  = (optimized.match(/^#{1,3}\s/gm) ?? []).length;
  if (optH > origH) {
    insights.push({ category: "Structure", icon: "🏗️", color: "indigo",
      change: `Added ${optH - origH} section header(s)`,
      why: "Headers help the model parse and organize its response into logical sections" });
  }

  // Clarity: bullets
  const origB = (original.match(/^[-*•]\s/gm) ?? []).length;
  const optB  = (optimized.match(/^[-*•]\s/gm) ?? []).length;
  if (optB > origB) {
    insights.push({ category: "Clarity", icon: "✨", color: "blue",
      change: `Converted prose to bullet points (+${optB - origB})`,
      why: "Bullet points are easier for AI to parse and produce consistent structured output" });
  }

  // Constraints
  const constraintWords = ["never", "always", "must", "only", "do not", "don't", "avoid", "ensure", "require", "strictly"];
  const origC = constraintWords.filter(w => original.toLowerCase().includes(w)).length;
  const optC  = constraintWords.filter(w => optimized.toLowerCase().includes(w)).length;
  if (optC > origC) {
    insights.push({ category: "Constraints", icon: "🎯", color: "green",
      change: "Added explicit constraints",
      why: "Clear constraints reduce hallucination and improve response consistency" });
  }

  // XML structure
  const xmlTags = ["<context>", "<instructions>", "<task>", "<output_format>", "<constraints>"];
  const hasXmlOpt  = xmlTags.some(t => optimized.includes(t));
  const hasXmlOrig = xmlTags.some(t => original.includes(t));
  if (hasXmlOpt && !hasXmlOrig) {
    insights.push({ category: "Format", icon: "📐", color: "purple",
      change: "Added XML section structure",
      why: "XML tags help Claude parse sections with significantly higher precision" });
  }

  // Role injection
  const rolePatterns = ["you are", "act as", "you're a", "as a senior", "as an expert"];
  const hasRoleOpt  = rolePatterns.some(p => optimized.toLowerCase().slice(0, 300).includes(p));
  const hasRoleOrig = rolePatterns.some(p => original.toLowerCase().slice(0, 300).includes(p));
  if (hasRoleOpt && !hasRoleOrig) {
    insights.push({ category: "Context", icon: "🎭", color: "orange",
      change: "Added role/persona injection",
      why: "Defining who the AI should be significantly improves expertise depth" });
  }

  // Efficiency
  if (optimized.length < original.length * 0.88) {
    const pct = Math.round((1 - optimized.length / original.length) * 100);
    insights.push({ category: "Efficiency", icon: "⚡", color: "yellow",
      change: `Removed ~${pct}% token overhead`,
      why: "Leaner prompts reduce cost and improve focus by eliminating noise" });
  }

  // Output format spec added
  const fmtWords = ["respond in", "format your", "structure your", "output as", "return a", "provide a"];
  const hasFmtOpt  = fmtWords.some(p => optimized.toLowerCase().includes(p));
  const hasFmtOrig = fmtWords.some(p => original.toLowerCase().includes(p));
  if (hasFmtOpt && !hasFmtOrig) {
    insights.push({ category: "Specificity", icon: "📋", color: "teal",
      change: "Added explicit output format specification",
      why: "Specifying the exact output format produces consistent, predictable results" });
  }

  return insights;
}
