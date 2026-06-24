import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";
import { ARCHITECT_SYSTEM_PROMPT } from "@/lib/prompts";

function parseArchitectOutput(raw: string) {
  const find = (label: string) => new RegExp(`##\\s*${label}\\s*\\n`, "i");

  const analysisM  = find("Prompt Analysis").exec(raw);
  const promptM    = find("Optimized Prompt").exec(raw);
  const enhanceM   = find("Enhancements Added").exec(raw);
  const scoreM     = find("Quality Score").exec(raw);

  const between = (a: RegExpExecArray | null, b: RegExpExecArray | null) =>
    a && b ? raw.slice(a.index + a[0].length, b.index).trim() : "";

  const analysis    = between(analysisM, promptM);
  const prompt      = between(promptM, enhanceM ?? scoreM) || (promptM ? raw.slice(promptM.index + promptM[0].length).trim() : raw);
  const enhancements = between(enhanceM, scoreM);
  const qualityScore = scoreM ? raw.slice(scoreM.index + scoreM[0].length).trim() : "";

  // Parse scores from table
  const scores: Record<string, number> = {};
  let total = 0;
  for (const line of qualityScore.split("\n")) {
    const m = /\|\s*\*?\*?([^|*]+?)\*?\*?\s*\|\s*\*?\*?(\d+)(?:\/10|\/100)?\*?\*?\s*\|/.exec(line);
    if (m) {
      const label = m[1].trim();
      const val   = parseInt(m[2], 10);
      if (label.toLowerCase().includes("total")) total = val;
      else scores[label] = val;
    }
  }
  if (!total) total = Object.values(scores).reduce((a, b) => a + b, 0);

  return { analysis, prompt, enhancements, qualityScore, scores, total };
}

export async function POST(req: NextRequest) {
  const { userRequest, platform, model } = await req.json() as {
    userRequest: string;
    platform: string;
    model?: string;
  };

  if (!userRequest?.trim() || !platform) {
    return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
  }

  const apiKey = process.env.GROQ_API_KEY ?? "";
  if (!apiKey) {
    return NextResponse.json({ error: "No AI backend configured. Add GROQ_API_KEY to environment." }, { status: 503 });
  }

  try {
    const client = new Groq({ apiKey });
    const res = await client.chat.completions.create({
      model: model ?? "llama-3.3-70b-versatile",
      messages: [
        { role: "system", content: ARCHITECT_SYSTEM_PROMPT },
        { role: "user",   content: `Target Platform: ${platform}\n\nUser Request:\n${userRequest}` },
      ],
      temperature: 0.3,
      max_tokens: 3000,
    });
    const raw = res.choices[0].message.content?.trim() ?? "";
    if (!raw) return NextResponse.json({ error: "Empty response from AI" }, { status: 502 });

    return NextResponse.json(parseArchitectOutput(raw));
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
