import { NextRequest, NextResponse } from "next/server";
import Groq from "groq-sdk";

export const runtime = "nodejs";
export const maxDuration = 60;

const ACTION_PROMPTS: Record<string, string | ((lang: string) => string)> = {
  clean:     "Clean and reformat this document. Normalize headings, lists, and spacing. Remove redundant blank lines and fix inconsistent formatting. Preserve all content exactly.",
  summarize: "Write a comprehensive summary of this document. Include the main topic, key points, and important details. Use clear headings and bullet points.",
  notes:     "Convert this document into concise, well-organized notes. Use Markdown with headings, subheadings, and bullet points. Focus on key information only.",
  readme:    "Convert this content into a professional GitHub README.md. Include sections: Overview, Features, Installation (if applicable), Usage, and Contributing. Use proper Markdown formatting.",
  actions:   "Extract all action items, tasks, decisions, and next steps from this document. Format as a numbered checklist. Group related items under category headings.",
  explain:   "Explain the content of this document clearly for someone unfamiliar with the topic. Use plain language, add context, and define any technical terms.",
  docs:      "Convert this content into professional technical documentation with sections: Overview, Description, Parameters or Fields (if applicable), Examples, and Notes. Be precise and complete.",
  translate: (lang: string) => `Translate this entire document to ${lang}. Preserve all headings, formatting, lists, and document structure exactly. Translate all text content.`,
  grammar:   "Fix all grammar, spelling, punctuation, and style errors in this document. Improve sentence clarity and flow. Preserve meaning, structure, and formatting.",
  study:     "Convert this document into comprehensive study notes. Include: Key Concepts (with definitions), Main Points, Important Details, and a Quick Review section at the end.",
  blog:      "Convert this content into an engaging blog article. Include a compelling introduction, well-structured sections with descriptive headings, and a conclusion. Use an accessible, conversational tone.",
  rewrite:   "Rewrite this document with improved clarity, flow, and professional tone. Fix awkward phrasing, improve word choice, and enhance readability. Preserve all key information and structure.",
};

export async function POST(req: NextRequest) {
  const apiKey = process.env.GROQ_API_KEY ?? "";
  if (!apiKey) {
    return NextResponse.json(
      { error: "AI enhancement requires GROQ_API_KEY. Add it in Vercel → Settings → Environment Variables." },
      { status: 503 },
    );
  }

  const { content, action, targetLanguage } = await req.json() as {
    content: string;
    action: string;
    targetLanguage?: string;
  };

  if (!content?.trim()) {
    return NextResponse.json({ error: "No content provided" }, { status: 400 });
  }

  const promptTemplate = ACTION_PROMPTS[action];
  if (!promptTemplate) {
    return NextResponse.json({ error: `Unknown action: ${action}` }, { status: 400 });
  }

  const systemPrompt = typeof promptTemplate === "function"
    ? promptTemplate(targetLanguage ?? "English")
    : promptTemplate;

  // Truncate content if too long (Groq context window ~32k tokens)
  const maxChars = 80_000;
  const truncated = content.length > maxChars
    ? content.slice(0, maxChars) + "\n\n[Document truncated for processing]"
    : content;

  const client = new Groq({ apiKey });
  const response = await client.chat.completions.create({
    model: "llama-3.3-70b-versatile",
    messages: [
      { role: "system", content: systemPrompt },
      { role: "user",   content: `Here is the document:\n\n${truncated}` },
    ],
    temperature: 0.3,
    max_tokens:  4096,
  });

  const enhanced = response.choices[0].message.content?.trim() ?? "";
  return NextResponse.json({ enhanced });
}
