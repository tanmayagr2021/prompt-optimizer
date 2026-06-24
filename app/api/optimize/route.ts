import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";
import { OPTIMIZER_SYSTEM_PROMPT } from "@/lib/prompts";
import { ruleOptimize } from "@/lib/optimizer";
import { analyzeChanges } from "@/lib/analyze-changes";

const PREAMBLE_RE = /^(here\s+is|here'?s|below\s+is|optimized\s+(prompt|version)|the\s+(optimized|rewritten|revised|improved)\s+(prompt|version)[:\s]*)/i;

function stripPreamble(text: string): string {
  const lines = text.split("\n");
  while (lines.length && PREAMBLE_RE.test(lines[0].trim())) lines.shift();
  return lines.join("\n").trim();
}

export async function POST(req: NextRequest) {
  const { prompt, model } = await req.json() as { prompt: string; model?: string };

  if (!prompt?.trim()) {
    return NextResponse.json({ error: "No prompt provided" }, { status: 400 });
  }

  const apiKey = process.env.GROQ_API_KEY ?? "";

  if (apiKey) {
    try {
      const client = new Groq({ apiKey });
      const res = await client.chat.completions.create({
        model: model ?? "llama-3.3-70b-versatile",
        messages: [
          { role: "system", content: OPTIMIZER_SYSTEM_PROMPT },
          { role: "user",   content: `Optimize this prompt:\n\n${prompt}` },
        ],
        temperature: 0.2,
        max_tokens: 2048,
      });
      const optimized = stripPreamble(res.choices[0].message.content?.trim() ?? "");
      if (optimized) {
        const insights = analyzeChanges(prompt, optimized);
        return NextResponse.json({ optimized, insights, mode: "ai", model: model ?? "llama-3.3-70b-versatile" });
      }
    } catch {
      // fall through to rule-based
    }
  }

  // Rule-based fallback
  const { optimized, mode } = ruleOptimize(prompt);
  const insights = analyzeChanges(prompt, optimized);
  return NextResponse.json({ optimized, insights, mode: `rule:${mode}` });
}
