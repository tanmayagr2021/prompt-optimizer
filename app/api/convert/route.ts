import { NextRequest, NextResponse } from "next/server";
import {
  detectFormat,
  formatLabel,
  extractContent,
  generateOutput,
  docStats,
  type OutputFormat,
} from "@/lib/converters";

export const runtime = "nodejs";
export const maxDuration = 60;

export async function POST(req: NextRequest) {
  let formData: FormData;
  try {
    formData = await req.formData();
  } catch {
    return NextResponse.json({ error: "Invalid form data" }, { status: 400 });
  }

  const file = formData.get("file");
  const outputFormat = (formData.get("outputFormat") as OutputFormat | null) ?? "md";

  if (!(file instanceof File)) {
    return NextResponse.json({ error: "No file provided" }, { status: 400 });
  }

  const MAX_SIZE = 15 * 1024 * 1024; // 15 MB
  if (file.size > MAX_SIZE) {
    return NextResponse.json({ error: `File too large. Maximum size is 15 MB.` }, { status: 413 });
  }

  const buffer = Buffer.from(await file.arrayBuffer());
  const inputFormat = detectFormat(file.name);
  const groqKey = process.env.GROQ_API_KEY ?? "";

  let extracted;
  try {
    extracted = await extractContent(buffer, inputFormat, groqKey);
  } catch (e) {
    return NextResponse.json(
      { error: `Extraction failed: ${e instanceof Error ? e.message : "unknown error"}` },
      { status: 500 },
    );
  }

  if (!extracted.text.trim()) {
    return NextResponse.json({ error: "No text could be extracted from this file." }, { status: 422 });
  }

  let generated;
  try {
    generated = await generateOutput(extracted.text, outputFormat, extracted.html);
  } catch (e) {
    return NextResponse.json(
      { error: `Output generation failed: ${e instanceof Error ? e.message : "unknown error"}` },
      { status: 500 },
    );
  }

  const baseName = file.name.replace(/\.[^.]+$/, "");
  // Second arg is the generated text for word/char count comparison; for binary formats use extracted.text as proxy
  const generatedText = ["docx", "pdf"].includes(outputFormat)
    ? extracted.text
    : generated.data.toString("utf-8");
  const stats = docStats(extracted.text, generatedText);

  return NextResponse.json({
    text:         extracted.text,
    outputBase64: generated.data.toString("base64"),
    mimeType:     generated.mimeType,
    ext:          generated.ext,
    fileName:     `${baseName}.${generated.ext}`,
    inputFormat:  inputFormat,
    inputLabel:   formatLabel(inputFormat),
    outputFormat: outputFormat,
    meta:         extracted.meta ?? {},
    stats,
  });
}
