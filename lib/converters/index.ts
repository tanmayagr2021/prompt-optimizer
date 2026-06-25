// Universal document conversion engine.
// All heavy libraries loaded dynamically — reduces cold-start overhead on Vercel.

export interface ExtractResult {
  text: string;
  html?: string;
  meta?: Record<string, string>;
}

export interface GenerateResult {
  data: Buffer;
  mimeType: string;
  ext: string;
}

export type InputFormat =
  | "pdf" | "docx" | "doc" | "pptx" | "ppt"
  | "xlsx" | "xls" | "csv" | "md" | "txt"
  | "html" | "epub" | "json" | "xml" | "image";

export type OutputFormat = "md" | "html" | "txt" | "csv" | "json" | "xml" | "docx" | "pdf";

// ─── FORMAT DETECTION ─────────────────────────────────────────────────────────

const EXT_MAP: Record<string, InputFormat> = {
  pdf: "pdf",
  doc: "doc", docx: "docx",
  ppt: "ppt", pptx: "pptx",
  xls: "xls", xlsx: "xlsx",
  csv: "csv",
  md: "md", markdown: "md",
  txt: "txt",
  html: "html", htm: "html",
  epub: "epub",
  json: "json",
  xml: "xml",
  png: "image", jpg: "image", jpeg: "image",
  webp: "image", gif: "image", bmp: "image",
  tiff: "image", tif: "image",
};

export function detectFormat(fileName: string): InputFormat {
  const ext = fileName.split(".").pop()?.toLowerCase() ?? "";
  return EXT_MAP[ext] ?? "txt";
}

export function formatLabel(format: InputFormat): string {
  const LABELS: Record<InputFormat, string> = {
    pdf: "PDF", docx: "Word (.docx)", doc: "Word (.doc)",
    pptx: "PowerPoint", ppt: "PowerPoint (legacy)",
    xlsx: "Excel", xls: "Excel (legacy)",
    csv: "CSV", md: "Markdown", txt: "Plain Text",
    html: "HTML", epub: "EPUB", json: "JSON", xml: "XML",
    image: "Image (OCR)",
  };
  return LABELS[format] ?? format.toUpperCase();
}

function wordCount(text: string): number {
  return text.trim().split(/\s+/).filter(Boolean).length;
}

export function docStats(original: string, converted: string) {
  return {
    inputChars:  original.length,
    outputChars: converted.length,
    inputWords:  wordCount(original),
    outputWords: wordCount(converted),
  };
}

// ─── EXTRACTION ───────────────────────────────────────────────────────────────

export async function extractContent(
  buffer: Buffer,
  format: InputFormat,
  groqKey?: string,
): Promise<ExtractResult> {
  switch (format) {
    case "pdf":   return extractPDF(buffer);
    case "docx":  return extractDOCX(buffer);
    case "doc":   return extractDOC(buffer);
    case "pptx":  return extractPPTX(buffer);
    case "ppt":   return { text: "[PPT (legacy) format: convert to .pptx for best results]" };
    case "xlsx":
    case "xls":   return extractXLSX(buffer);
    case "csv":   return { text: buffer.toString("utf-8") };
    case "md":    return extractMarkdown(buffer);
    case "txt":   return { text: buffer.toString("utf-8") };
    case "html":  return extractHTML(buffer);
    case "epub":  return extractEPUB(buffer);
    case "json":  return extractJSON(buffer);
    case "xml":   return { text: buffer.toString("utf-8") };
    case "image":
      if (!groqKey) {
        return { text: "[Image OCR requires GROQ_API_KEY in environment variables.]" };
      }
      return extractImageOCR(buffer, groqKey);
    default:
      return { text: buffer.toString("utf-8") };
  }
}

async function extractPDF(buffer: Buffer): Promise<ExtractResult> {
  try {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const pdfParse = require("pdf-parse") as (buf: Buffer) => Promise<{ text: string; numpages: number }>;
    const data = await pdfParse(buffer);
    return { text: data.text.trim(), meta: { pages: String(data.numpages) } };
  } catch {
    return {
      text: "[PDF text extraction failed. The file may be image-only or password-protected. Try uploading as an image for OCR.]",
    };
  }
}

async function extractDOCX(buffer: Buffer): Promise<ExtractResult> {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const mammoth = require("mammoth") as {
    extractRawText: (o: { buffer: Buffer }) => Promise<{ value: string }>;
    convertToHtml:  (o: { buffer: Buffer }) => Promise<{ value: string }>;
  };
  const [raw, htmlRes] = await Promise.all([
    mammoth.extractRawText({ buffer }),
    mammoth.convertToHtml({ buffer }),
  ]);
  return { text: raw.value.trim(), html: htmlRes.value };
}

function extractDOC(buffer: Buffer): ExtractResult {
  // Binary .doc: salvage readable ASCII fragments (crude but often effective for simple files)
  const str = buffer.toString("latin1");
  const text = str
    .replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\xFF]/g, " ")
    .replace(/ {5,}/g, "\n")
    .split("\n")
    .filter(l => l.trim().length > 4)
    .join("\n")
    .trim();
  return {
    text: text.length > 50
      ? text
      : "[Could not extract text from .doc (legacy binary). Convert to .docx for accurate extraction.]",
  };
}

async function extractPPTX(buffer: Buffer): Promise<ExtractResult> {
  const JSZip = (await import("jszip")).default;
  const zip = await JSZip.loadAsync(buffer);

  const slideFiles = Object.keys(zip.files)
    .filter(f => /^ppt\/slides\/slide\d+\.xml$/.test(f))
    .sort((a, b) => {
      const na = parseInt(a.match(/(\d+)/)?.[0] ?? "0");
      const nb = parseInt(b.match(/(\d+)/)?.[0] ?? "0");
      return na - nb;
    });

  const slides: string[] = [];
  for (let i = 0; i < slideFiles.length; i++) {
    const xml = await zip.files[slideFiles[i]].async("string");
    const texts: string[] = [];
    const re = /<a:t[^>]*>([^<]*)<\/a:t>/g;
    let m: RegExpExecArray | null;
    while ((m = re.exec(xml)) !== null) {
      if (m[1].trim()) texts.push(m[1].trim());
    }
    if (texts.length) slides.push(`## Slide ${i + 1}\n\n${texts.join(" ")}`);
  }

  return { text: slides.join("\n\n") || "[No readable text found in presentation]" };
}

async function extractXLSX(buffer: Buffer): Promise<ExtractResult> {
  const XLSX = await import("xlsx");
  const workbook = XLSX.read(buffer, { type: "buffer" });
  const parts: string[] = [];

  for (const sheetName of workbook.SheetNames) {
    const sheet = workbook.Sheets[sheetName];
    const csv = XLSX.utils.sheet_to_csv(sheet);
    if (csv.trim()) parts.push(`## ${sheetName}\n\n${csv}`);
  }

  return { text: parts.join("\n\n") };
}

async function extractMarkdown(buffer: Buffer): Promise<ExtractResult> {
  const text = buffer.toString("utf-8");
  const { marked } = await import("marked");
  const html = await marked(text);
  return { text, html };
}

async function extractHTML(buffer: Buffer): Promise<ExtractResult> {
  const html = buffer.toString("utf-8");
  const TurndownService = (await import("turndown")).default;
  const td = new TurndownService({ headingStyle: "atx", bulletListMarker: "-" });
  const text = td.turndown(html);
  return { text, html };
}

async function extractEPUB(buffer: Buffer): Promise<ExtractResult> {
  const JSZip = (await import("jszip")).default;
  const TurndownService = (await import("turndown")).default;
  const td = new TurndownService({ headingStyle: "atx", bulletListMarker: "-" });

  const zip = await JSZip.loadAsync(buffer);
  const htmlFiles = Object.keys(zip.files)
    .filter(f => (f.endsWith(".html") || f.endsWith(".xhtml")) && !f.includes("__MACOSX"))
    .sort();

  const parts: string[] = [];
  for (const fname of htmlFiles) {
    const content = await zip.files[fname].async("string");
    const bodyMatch = content.match(/<body[^>]*>([\s\S]*?)<\/body>/i);
    const body = bodyMatch ? bodyMatch[1] : content;
    const md = td.turndown(body);
    if (md.trim().length > 20) parts.push(md.trim());
  }

  return { text: parts.join("\n\n---\n\n") };
}

function extractJSON(buffer: Buffer): ExtractResult {
  try {
    const obj = JSON.parse(buffer.toString("utf-8"));
    return { text: JSON.stringify(obj, null, 2) };
  } catch {
    return { text: buffer.toString("utf-8") };
  }
}

async function extractImageOCR(buffer: Buffer, groqKey: string): Promise<ExtractResult> {
  const Groq = (await import("groq-sdk")).default;
  const client = new Groq({ apiKey: groqKey });

  // Detect image MIME from magic bytes
  const magic = buffer.slice(0, 4);
  let mimeType = "image/jpeg";
  if (magic[0] === 0x89 && magic[1] === 0x50) mimeType = "image/png";
  else if (magic[0] === 0x47 && magic[1] === 0x49) mimeType = "image/gif";
  else if (magic[0] === 0x52 && magic[1] === 0x49) mimeType = "image/webp";

  const base64 = buffer.toString("base64");

  const response = await client.chat.completions.create({
    model: "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    messages: [
      {
        role: "user",
        content: [
          {
            type: "image_url",
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            image_url: { url: `data:${mimeType};base64,${base64}` } as any,
          },
          {
            type: "text",
            text: "Extract ALL text from this image. Preserve headings, lists, tables, and formatting as accurately as possible using Markdown. Return only the extracted text — no commentary, no preamble.",
          },
        ],
      },
    ],
    max_tokens: 4096,
    temperature: 0.1,
  });

  return { text: response.choices[0].message.content?.trim() ?? "" };
}

// ─── GENERATION ───────────────────────────────────────────────────────────────

export async function generateOutput(
  text: string,
  format: OutputFormat,
  sourceHtml?: string,
): Promise<GenerateResult> {
  switch (format) {
    case "md":   return generateMarkdown(text, sourceHtml);
    case "html": return generateHTML(text, sourceHtml);
    case "txt":  return { data: Buffer.from(text, "utf-8"), mimeType: "text/plain", ext: "txt" };
    case "csv":  return generateCSV(text);
    case "json": return generateJSON(text);
    case "xml":  return generateXML(text);
    case "docx": return generateDOCX(text);
    case "pdf":  return generatePDF(text);
  }
}

async function generateMarkdown(text: string, sourceHtml?: string): Promise<GenerateResult> {
  let md = text;
  if (sourceHtml?.trim()) {
    const TurndownService = (await import("turndown")).default;
    const td = new TurndownService({ headingStyle: "atx", bulletListMarker: "-", codeBlockStyle: "fenced" });
    md = td.turndown(sourceHtml);
  }
  return { data: Buffer.from(md, "utf-8"), mimeType: "text/markdown", ext: "md" };
}

async function generateHTML(text: string, sourceHtml?: string): Promise<GenerateResult> {
  let body: string;
  if (sourceHtml?.trim()) {
    body = sourceHtml;
  } else {
    const { marked } = await import("marked");
    body = await marked(text);
  }

  const html = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Converted Document</title>
  <style>
    body { font-family: Georgia, serif; max-width: 820px; margin: 0 auto; padding: 48px 24px; line-height: 1.75; color: #1b1c19; background: #fbf9f4; }
    h1, h2, h3, h4 { font-weight: 700; margin-top: 2em; margin-bottom: 0.5em; }
    h1 { font-size: 2em; } h2 { font-size: 1.5em; } h3 { font-size: 1.25em; }
    p { margin: 0.75em 0; }
    pre { background: #f5f3ee; border: 1px solid #e2beba; padding: 16px; border-radius: 6px; overflow-x: auto; font-family: monospace; font-size: 0.9em; }
    code { background: #f5f3ee; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; font-family: monospace; }
    table { border-collapse: collapse; width: 100%; margin: 1em 0; }
    th, td { border: 1px solid #e2beba; padding: 8px 14px; text-align: left; }
    th { background: #f5f3ee; font-weight: 600; }
    blockquote { border-left: 3px solid #8f000d; margin: 1em 0; padding: 0.5em 1em; color: #5a403e; }
    ul, ol { padding-left: 1.75em; }
    li { margin: 0.3em 0; }
    hr { border: none; border-top: 1px solid #e2beba; margin: 2em 0; }
  </style>
</head>
<body>${body}</body>
</html>`;

  return { data: Buffer.from(html, "utf-8"), mimeType: "text/html", ext: "html" };
}

function generateCSV(text: string): GenerateResult {
  const lines = text.split("\n");
  const looksLikeCSV = lines.slice(0, 5).filter(l => l.trim()).every(l => l.includes(","));
  const csv = looksLikeCSV
    ? text
    : lines.map(l => `"${l.replace(/"/g, '""')}"`).join("\n");
  return { data: Buffer.from(csv, "utf-8"), mimeType: "text/csv", ext: "csv" };
}

function generateJSON(text: string): GenerateResult {
  let payload: unknown;
  try {
    payload = JSON.parse(text);
  } catch {
    payload = { content: text, lines: text.split("\n").filter(Boolean) };
  }
  return {
    data: Buffer.from(JSON.stringify(payload, null, 2), "utf-8"),
    mimeType: "application/json",
    ext: "json",
  };
}

function generateXML(text: string): GenerateResult {
  const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<document>\n  <content><![CDATA[${text}]]></content>\n</document>`;
  return { data: Buffer.from(xml, "utf-8"), mimeType: "application/xml", ext: "xml" };
}

async function generateDOCX(text: string): Promise<GenerateResult> {
  const { Document, Packer, Paragraph, TextRun, HeadingLevel } = await import("docx");

  const children = text.split("\n").map(line => {
    if (line.startsWith("### ")) {
      return new Paragraph({ text: line.slice(4).trim(), heading: HeadingLevel.HEADING_3 });
    } else if (line.startsWith("## ")) {
      return new Paragraph({ text: line.slice(3).trim(), heading: HeadingLevel.HEADING_2 });
    } else if (line.startsWith("# ")) {
      return new Paragraph({ text: line.slice(2).trim(), heading: HeadingLevel.HEADING_1 });
    } else if (/^[-*]\s/.test(line)) {
      return new Paragraph({ children: [new TextRun({ text: `• ${line.slice(2).trim()}` })] });
    } else if (/^\d+\.\s/.test(line)) {
      return new Paragraph({ children: [new TextRun({ text: line })] });
    } else if (line.trim() === "") {
      return new Paragraph({ text: "" });
    } else {
      return new Paragraph({ children: [new TextRun({ text: line })] });
    }
  });

  const doc = new Document({ sections: [{ children }] });
  const buffer = await Packer.toBuffer(doc);

  return {
    data: buffer,
    mimeType: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ext: "docx",
  };
}

async function generatePDF(text: string): Promise<GenerateResult> {
  const { PDFDocument, StandardFonts, rgb } = await import("pdf-lib");

  const pdfDoc = await PDFDocument.create();
  const regular = await pdfDoc.embedFont(StandardFonts.Helvetica);
  const bold    = await pdfDoc.embedFont(StandardFonts.HelveticaBold);

  const W = 612, H = 792, M = 60;
  const TEXT_W = W - M * 2;
  const BASE = 11, LH = 18;

  let page = pdfDoc.addPage([W, H]);
  let y = H - M;

  function ensureSpace(h: number) {
    if (y - h < M) { page = pdfDoc.addPage([W, H]); y = H - M; }
  }

  function drawLine(raw: string, font: typeof regular, size: number, indent = 0) {
    // Sanitize to printable ASCII (pdf-lib Standard fonts are WinAnsi)
    const s = raw.replace(/[^\x20-\x7E]/g, char => {
      const replacements: Record<string, string> = {
        "‘": "'", "’": "'", "“": '"', "”": '"',
        "–": "-", "—": "--", "…": "...", " ": " ",
      };
      return replacements[char] ?? "";
    });

    if (!s.trim()) { y -= LH * 0.5; return; }

    const words = s.split(" ");
    let row = "";
    const maxW = TEXT_W - indent;

    for (const word of words) {
      const test = row ? `${row} ${word}` : word;
      if (font.widthOfTextAtSize(test, size) > maxW && row) {
        ensureSpace(LH);
        page.drawText(row, { x: M + indent, y, size, font, color: rgb(0.1, 0.1, 0.1) });
        y -= LH;
        row = word;
      } else {
        row = test;
      }
    }
    if (row) {
      ensureSpace(LH);
      page.drawText(row, { x: M + indent, y, size, font, color: rgb(0.1, 0.1, 0.1) });
      y -= LH;
    }
  }

  for (const line of text.split("\n")) {
    if (line.startsWith("# ")) {
      y -= 8; drawLine(line.slice(2), bold, 20); y -= 4;
    } else if (line.startsWith("## ")) {
      y -= 6; drawLine(line.slice(3), bold, 16); y -= 2;
    } else if (line.startsWith("### ")) {
      y -= 4; drawLine(line.slice(4), bold, 13);
    } else if (/^[-*]\s/.test(line)) {
      drawLine(`• ${line.slice(2)}`, regular, BASE, 12);
    } else if (line.trim() === "") {
      y -= LH * 0.4;
    } else {
      drawLine(line, regular, BASE);
    }
  }

  const bytes = await pdfDoc.save();
  return { data: Buffer.from(bytes), mimeType: "application/pdf", ext: "pdf" };
}
