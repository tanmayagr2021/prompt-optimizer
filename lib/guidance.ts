import type { Tip, LearnItem } from "./types";

export const TIPS: Tip[] = [
  { id: "xml_claude", type: "Pro Tip", icon: "💡", title: "XML tags supercharge Claude",
    body: "Claude was trained with XML-structured prompts. Wrapping sections in <context>, <instructions>, and <output_format> tags can improve response quality by 30–50%.",
    platform: "Claude", trigger: "architect_Claude" },
  { id: "constraints", type: "Best Practice", icon: "🎯", title: "Add constraints, improve reliability",
    body: "Explicit constraints (\"always\", \"never\", \"maximum X words\") reduce hallucination and improve output consistency significantly in production settings.",
    trigger: "always" },
  { id: "markdown_workflow", type: "Workflow", icon: "📄", title: "Large report? Use the Markdown export",
    body: "Download as Markdown and upload to a fresh AI conversation to reduce context size. Especially powerful for Claude Projects and long-form research workflows.",
    trigger: "after_optimize" },
  { id: "gpt_system", type: "Pro Tip", icon: "💡", title: "System prompts are GPT's most powerful lever",
    body: "ChatGPT performs best when instructions are in the system prompt and content is in the user message. Splitting these consistently improves response quality.",
    platform: "ChatGPT", trigger: "architect_ChatGPT" },
  { id: "role_injection", type: "Best Practice", icon: "🎭", title: "Be specific with role injection",
    body: "\"You are a senior product manager at a B2B SaaS startup\" dramatically outperforms \"You are a product manager\". The more specific the role, the higher the expertise level.",
    trigger: "always" },
  { id: "few_shot", type: "Pro Tip", icon: "📋", title: "Examples outperform long instructions",
    body: "3 concrete input/output examples are more effective than a paragraph of instructions. AI models learn format, tone, and style from examples far better than rules.",
    trigger: "always" },
  { id: "cot", type: "Best Practice", icon: "🔗", title: "Chain-of-thought for complex reasoning",
    body: "Adding \"Think step by step\" dramatically improves accuracy on multi-step reasoning and analysis tasks. Claude and GPT-4 have built-in reasoning you can activate this way.",
    trigger: "always" },
  { id: "token_efficiency", type: "Insight", icon: "⚡", title: "Shorter prompts often produce better results",
    body: "Optimizing for token efficiency isn't just about cost — leaner prompts reduce ambiguity and help the model focus on what actually matters.",
    trigger: "after_optimize" },
  { id: "cursor_files", type: "Pro Tip", icon: "💡", title: "Reference files explicitly in Cursor",
    body: "In Cursor and Windsurf, \"In @auth.ts, implement JWT refresh\" is dramatically more effective than \"implement token refresh\".",
    platform: "Cursor", trigger: "architect_Cursor" },
  { id: "midjourney_style", type: "Pro Tip", icon: "🎨", title: "Style references transform image quality",
    body: "Adding \"in the style of [artist/era/medium]\" is one of the highest-leverage changes in Midjourney. Combine 2–3 style references for unique aesthetics.",
    platform: "Midjourney", trigger: "architect_Midjourney" },
  { id: "perplexity_cite", type: "Best Practice", icon: "📚", title: "Always ask Perplexity to cite sources",
    body: "Include \"cite sources with URLs\" in every Perplexity prompt. This ensures verifiability and significantly improves research output quality.",
    platform: "Perplexity", trigger: "architect_Perplexity" },
  { id: "output_format", type: "Did You Know", icon: "📐", title: "Define output format explicitly",
    body: "Specifying the exact format you want — JSON, markdown table, numbered list, structured report — prevents the model from guessing and gives you consistent outputs.",
    trigger: "always" },
  { id: "negative_space", type: "Insight", icon: "🚫", title: "Tell AI what NOT to do",
    body: "Negative constraints are often more powerful than positive ones. \"Do not include preamble\", \"Never use passive voice\" shapes outputs as much as positive instructions.",
    trigger: "always" },
  { id: "gemini_grounding", type: "Did You Know", icon: "🔍", title: "Gemini excels with grounded context",
    body: "When working with Gemini, provide factual, specific context and reference sources explicitly. Gemini's reasoning improves significantly with concrete grounding.",
    platform: "Gemini", trigger: "architect_Gemini" },
  { id: "sd_negative", type: "Pro Tip", icon: "🎨", title: "Negative prompts are critical in Stable Diffusion",
    body: "A strong negative prompt (\"blurry, low quality, distorted, watermark\") is as important as your main prompt. Always include one for professional results.",
    platform: "Stable Diffusion", trigger: "architect_Stable Diffusion" },
];

export const EXAMPLE_PROMPTS = [
  "You are a senior product manager. Write a detailed PRD for a B2B invoicing automation feature...",
  "Analyze the competitive landscape for AI coding assistants in 2024. Focus on differentiation...",
  "You are a data scientist. Explain gradient boosting to a non-technical executive audience...",
  "Write a technical architecture document for a real-time collaborative editing system...",
  "Create a comprehensive marketing strategy for launching a developer tool to a startup audience...",
];

export function getContextualTip(context: string, platform?: string): Tip {
  const weighted: Array<{ tip: Tip; weight: number }> = [];
  for (const tip of TIPS) {
    if (tip.trigger === "always")          weighted.push({ tip, weight: 1 });
    if (tip.trigger === context)           weighted.push({ tip, weight: 3 });
    if (platform && tip.platform === platform) weighted.push({ tip, weight: 2 });
  }
  if (!weighted.length) return TIPS[Math.floor(Math.random() * TIPS.length)];
  const pool = weighted.flatMap(({ tip, weight }) => Array(weight).fill(tip) as Tip[]);
  return pool[Math.floor(Math.random() * pool.length)];
}

export function getRandomTips(count: number): Tip[] {
  const shuffled = [...TIPS].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, Math.min(count, TIPS.length));
}

export function getRandomExample(): string {
  return EXAMPLE_PROMPTS[Math.floor(Math.random() * EXAMPLE_PROMPTS.length)];
}

export const LEARN_CONTENT: Record<string, LearnItem[]> = {
  Basics: [
    { title: "What Is Prompt Engineering?", icon: "🧠", difficulty: "Beginner", readTime: "3 min",
      summary: "Prompt engineering is the practice of designing AI model inputs to produce optimal outputs. Think of it like writing a precise brief for a contractor — clarity, context, and constraints are everything.",
      keyPoints: ["Be specific — vague prompts produce vague results", "Provide relevant background context before the task", "Define exactly what the output should look like", "Add constraints to guide and bound the response", "Iterate and refine based on what you observe"] },
    { title: "The Anatomy of a Great Prompt", icon: "🔬", difficulty: "Beginner", readTime: "4 min",
      summary: "Every high-quality prompt contains five elements: Role, Context, Task, Format, and Constraints. Missing any one of them is usually why prompts underperform.",
      keyPoints: ["Role: Who should the AI be? Define expertise and perspective", "Context: What background does it need to know?", "Task: What exactly are you asking it to do?", "Format: How should the output be structured?", "Constraints: What should it avoid, limit, or always include?"] },
    { title: "Zero-Shot vs Few-Shot Prompting", icon: "📊", difficulty: "Intermediate", readTime: "5 min",
      summary: "Zero-shot gives instructions only. Few-shot provides examples. Few-shot almost always outperforms zero-shot for complex tasks — 3–5 examples is usually the sweet spot.",
      keyPoints: ["Zero-shot: instructions only — works for simple tasks", "One-shot: one example — great for format and tone guidance", "Few-shot: 3–5 examples — best for complex outputs", "Examples should span the range of inputs you expect", "Negative examples (what NOT to produce) are also effective"] },
    { title: "Chain-of-Thought Prompting", icon: "🔗", difficulty: "Intermediate", readTime: "4 min",
      summary: "Asking the AI to reason step-by-step before answering dramatically improves accuracy on complex reasoning, math, and multi-step analysis tasks.",
      keyPoints: ["Add \"Think step by step\" for reasoning tasks", "Improves accuracy by 20–40% on hard problems", "Works best combined with few-shot examples", "Claude, GPT-4, and Gemini all have built-in reasoning you can activate", "Use \"Reason carefully before answering\" for nuanced topics"] },
    { title: "Prompt Iteration Strategies", icon: "🔄", difficulty: "Intermediate", readTime: "5 min",
      summary: "The first prompt is rarely the best one. Systematic iteration — not random tweaking — is how professional prompt engineers improve their results.",
      keyPoints: ["Change one thing at a time to isolate improvements", "Keep a log of what you tried and what worked", "Test on edge cases, not just typical inputs", "Ask the AI to critique its own output and improve it", "Think of prompt quality like code quality — it compounds"] },
  ],
  Claude: [
    { title: "Claude Prompt Best Practices", icon: "🟣", difficulty: "Intermediate", readTime: "6 min",
      summary: "Claude is optimized for nuanced reasoning and following complex instructions. It responds best to structured, explicit, context-rich prompts with XML tags.",
      keyPoints: ["Use XML tags: <context>, <task>, <format>, <constraints>", "Claude respects explicit constraints exceptionally well", "Add 'Think carefully before answering' for complex tasks", "Claude handles 200K+ token context windows — use them", "Be explicit about every edge case"] },
    { title: "XML Structure for Claude", icon: "📐", difficulty: "Advanced", readTime: "5 min",
      summary: "Claude was trained with XML-tagged prompts and responds measurably better when sections are wrapped in XML. This is the single highest-leverage technique.",
      keyPoints: ["<context>: Background information and existing state", "<instructions>: What Claude should do, step by step", "<examples>: Input/output pairs demonstrating the format", "<output_format>: The exact structure you expect", "<constraints>: Hard rules (use NEVER/ALWAYS)"] },
  ],
  ChatGPT: [
    { title: "ChatGPT Prompt Best Practices", icon: "🟢", difficulty: "Intermediate", readTime: "5 min",
      summary: "ChatGPT responds best to role-playing, step-by-step instructions, and explicit output formats. The system prompt is your most powerful tool.",
      keyPoints: ["Use system prompts for all persistent instructions", "Role injection: 'You are a senior [specific expert]...'", "Request JSON output for structured data extraction", "Ask for reasoning before conclusions on analytical tasks", "GPT-4o excels at code, analysis, and multimodal tasks"] },
  ],
  Gemini: [
    { title: "Gemini Prompt Best Practices", icon: "🔵", difficulty: "Intermediate", readTime: "5 min",
      summary: "Gemini performs best with grounded, factual contexts. It excels at long-context tasks and benefits from explicit structure.",
      keyPoints: ["Provide factual, grounded context", "Reference specific sources when available", "Gemini 1.5 Pro handles 1M+ token contexts", "Use step-by-step breakdowns for complex reasoning", "Ask for structured outputs — tables, JSON, numbered lists"] },
  ],
  Research: [
    { title: "Research Prompt Templates", icon: "🔍", difficulty: "Intermediate", readTime: "7 min",
      summary: "Effective research prompts are built around four pillars: question, scope, methodology, and output format.",
      keyPoints: ["Define the research question with precision", "Specify scope: time range, geography, industry", "Request citations and source URLs explicitly", "Ask for competing perspectives and counterarguments", "Structure: executive summary → findings → evidence → recommendations"] },
    { title: "Using Perplexity Effectively", icon: "🔎", difficulty: "Beginner", readTime: "4 min",
      summary: "Perplexity is optimized for real-time web research with citations. Treat it like a research assistant, not a chatbot.",
      keyPoints: ["Always request source citations with URLs", "Specify recency: 'from the last 6 months only'", "Ask Perplexity to compare sources, not just summarize", "Follow up with 'What are the counterarguments?'", "Use for current events, market data, and fact-checking"] },
  ],
  Coding: [
    { title: "Coding Prompt Best Practices", icon: "💻", difficulty: "Intermediate", readTime: "6 min",
      summary: "Effective coding prompts provide language/framework context, existing code, specific requirements, and desired output structure — all together.",
      keyPoints: ["Always specify language, framework, and version", "Include relevant existing code for context", "Describe the problem, not just the solution", "Request error handling, edge cases, and tests", "Ask for comments explaining non-obvious logic"] },
    { title: "Cursor & Windsurf Agent Best Practices", icon: "⬛", difficulty: "Advanced", readTime: "5 min",
      summary: "IDE coding agents work best with explicit file references, full task context, and incremental change requests.",
      keyPoints: ["Reference specific files with @filename", "Describe the full change context, not just the end state", "Request one logical change at a time", "Ask for tests alongside implementations", "Use .cursorrules for persistent project context"] },
  ],
  Product: [
    { title: "Product Management Prompts", icon: "📋", difficulty: "Intermediate", readTime: "6 min",
      summary: "PM prompts should include: product context, user persona, business constraints, success metrics, and the exact artifact you need.",
      keyPoints: ["Define the product, market, and target user with specificity", "Include relevant metrics and business context", "Specify the exact artifact: PRD, user story, OKR, roadmap", "Ask for prioritization rationale alongside recommendations", "Request both qualitative and quantitative success criteria"] },
  ],
  Marketing: [
    { title: "Marketing Prompt Templates", icon: "📣", difficulty: "Beginner", readTime: "5 min",
      summary: "Marketing prompts need: brand voice definition, target audience, channel context, and clear calls-to-action.",
      keyPoints: ["Define brand voice with 3–5 specific adjectives", "Specify target audience with psychographics", "Include the channel context (LinkedIn vs email vs landing page)", "Provide a tone example: 'Write in a style similar to...'", "Always ask for 3+ variants — the first is rarely the best"] },
  ],
  Academic: [
    { title: "Academic Research Prompts", icon: "🎓", difficulty: "Advanced", readTime: "7 min",
      summary: "Academic prompts require precise language, source quality specifications, citation styles, and structured argumentation.",
      keyPoints: ["Specify citation style: APA 7, MLA 9, Chicago 17", "Request peer-reviewed sources — specify primary research", "Define the argumentation structure: thesis, evidence, conclusion", "Ask for counterarguments and acknowledged limitations", "Specify academic level: undergrad, grad, doctoral, journal-quality"] },
  ],
};
