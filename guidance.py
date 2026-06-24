"""
Guidance system — tips, learning content, and platform advice.
"""

import random
from typing import Optional

# ── Tips database ─────────────────────────────────────────────────────────────

TIPS = [
    {
        "id": "xml_claude",
        "type": "Pro Tip",
        "icon": "💡",
        "title": "XML tags supercharge Claude",
        "body": "Claude was trained with XML-structured prompts. Wrapping sections in <context>, <instructions>, and <output_format> tags can improve response quality by 30–50%.",
        "platform": "Claude",
        "category": "structure",
        "trigger": "architect_claude",
    },
    {
        "id": "constraints_reliability",
        "type": "Best Practice",
        "icon": "🎯",
        "title": "Add constraints, improve reliability",
        "body": "Explicit constraints (\"always\", \"never\", \"maximum X words\") reduce hallucination and improve output consistency significantly in production settings.",
        "platform": None,
        "category": "reliability",
        "trigger": "always",
    },
    {
        "id": "markdown_workflow",
        "type": "Workflow",
        "icon": "📄",
        "title": "Large report? Use the Markdown export",
        "body": "Download as Markdown and upload to a fresh AI conversation to reduce context size. This is especially powerful for Claude Projects and long-form research workflows.",
        "platform": None,
        "category": "efficiency",
        "trigger": "after_optimize",
    },
    {
        "id": "gpt_system_prompt",
        "type": "Pro Tip",
        "icon": "💡",
        "title": "System prompts are GPT's most powerful lever",
        "body": "ChatGPT performs best when instructions are in the system prompt and content is in the user message. Splitting these consistently improves response quality.",
        "platform": "ChatGPT",
        "category": "structure",
        "trigger": "architect_ChatGPT",
    },
    {
        "id": "gemini_grounding",
        "type": "Did You Know",
        "icon": "🔍",
        "title": "Gemini excels with grounded context",
        "body": "When working with Gemini, provide factual, specific context and reference sources explicitly. Gemini's reasoning improves significantly with concrete grounding.",
        "platform": "Gemini",
        "category": "platform",
        "trigger": "architect_Gemini",
    },
    {
        "id": "role_injection",
        "type": "Best Practice",
        "icon": "🎭",
        "title": "Be specific with role injection",
        "body": "\"You are a senior product manager at a B2B SaaS startup\" dramatically outperforms \"You are a product manager\". The more specific the role, the higher the expertise level.",
        "platform": None,
        "category": "structure",
        "trigger": "always",
    },
    {
        "id": "few_shot_examples",
        "type": "Pro Tip",
        "icon": "📋",
        "title": "Examples outperform long instructions",
        "body": "3 concrete input/output examples are more effective than a paragraph of instructions. AI models learn format, tone, and style from examples far better than rules.",
        "platform": None,
        "category": "technique",
        "trigger": "always",
    },
    {
        "id": "chain_of_thought",
        "type": "Best Practice",
        "icon": "🔗",
        "title": "Chain-of-thought for complex reasoning",
        "body": "Adding \"Think step by step\" or \"Reason through this carefully before answering\" dramatically improves accuracy on multi-step reasoning and analysis tasks.",
        "platform": None,
        "category": "technique",
        "trigger": "always",
    },
    {
        "id": "token_efficiency",
        "type": "Insight",
        "icon": "⚡",
        "title": "Shorter prompts often produce better results",
        "body": "Optimizing for token efficiency isn't just about cost — leaner, cleaner prompts reduce ambiguity and help the model focus on what actually matters.",
        "platform": None,
        "category": "efficiency",
        "trigger": "after_optimize",
    },
    {
        "id": "cursor_file_refs",
        "type": "Pro Tip",
        "icon": "💡",
        "title": "Reference files explicitly in Cursor",
        "body": "In Cursor and Windsurf, \"In @auth.ts, implement JWT refresh\" is dramatically more effective than \"implement token refresh\". File context is your highest-leverage input.",
        "platform": "Cursor",
        "category": "platform",
        "trigger": "architect_Cursor",
    },
    {
        "id": "midjourney_style",
        "type": "Pro Tip",
        "icon": "🎨",
        "title": "Style references transform image quality",
        "body": "Adding \"in the style of [artist/era/medium]\" is one of the highest-leverage changes in Midjourney. Combine 2–3 style references for unique, consistent aesthetics.",
        "platform": "Midjourney",
        "category": "platform",
        "trigger": "architect_Midjourney",
    },
    {
        "id": "perplexity_citations",
        "type": "Best Practice",
        "icon": "📚",
        "title": "Always ask Perplexity to cite sources",
        "body": "Include \"cite sources with URLs\" in every Perplexity prompt. This ensures verifiability and significantly improves research output quality and trust.",
        "platform": "Perplexity",
        "category": "platform",
        "trigger": "architect_Perplexity",
    },
    {
        "id": "output_format",
        "type": "Did You Know",
        "icon": "📐",
        "title": "Define output format explicitly",
        "body": "Specifying the exact format you want — JSON, markdown table, numbered list, structured report — prevents the model from guessing and gives you consistent outputs.",
        "platform": None,
        "category": "structure",
        "trigger": "always",
    },
    {
        "id": "negative_space",
        "type": "Insight",
        "icon": "🚫",
        "title": "Tell AI what NOT to do",
        "body": "Negative constraints are often more powerful than positive ones. \"Do not include preamble\", \"Never use passive voice\", \"Skip the summary\" shapes outputs as much as positive instructions.",
        "platform": None,
        "category": "technique",
        "trigger": "always",
    },
    {
        "id": "stable_diffusion_neg",
        "type": "Pro Tip",
        "icon": "🎨",
        "title": "Negative prompts are critical in Stable Diffusion",
        "body": "A strong negative prompt (\"blurry, low quality, distorted, watermark\") is as important as your main prompt. Always include one for professional results.",
        "platform": "Stable Diffusion",
        "category": "platform",
        "trigger": "architect_Stable Diffusion",
    },
]

EXAMPLE_PROMPTS = [
    "You are a senior product manager. Write a detailed PRD for a B2B invoicing automation feature...",
    "Analyze the competitive landscape for AI coding assistants in 2024. Focus on differentiation...",
    "You are a data scientist. Explain gradient boosting to a non-technical executive audience...",
    "Write a technical architecture document for a real-time collaborative editing system...",
    "Create a comprehensive marketing strategy for launching a developer tool to a startup audience...",
    "You are a UX researcher. Provide a detailed critique of this onboarding flow and suggest improvements...",
]

# ── Learning content ──────────────────────────────────────────────────────────

LEARNING_CONTENT = {
    "Basics": [
        {
            "title": "What Is Prompt Engineering?",
            "icon": "🧠",
            "difficulty": "Beginner",
            "read_time": "3 min",
            "summary": "Prompt engineering is the practice of designing AI model inputs to produce optimal outputs. Think of it like writing a precise brief for a contractor — clarity, context, and constraints are everything.",
            "key_points": [
                "Be specific about what you want — vague prompts produce vague results",
                "Provide relevant background context before the task",
                "Define exactly what the output should look like",
                "Add constraints to guide and bound the response",
                "Iterate and refine based on what you observe",
            ],
        },
        {
            "title": "The Anatomy of a Great Prompt",
            "icon": "🔬",
            "difficulty": "Beginner",
            "read_time": "4 min",
            "summary": "Every high-quality prompt contains five elements: Role, Context, Task, Format, and Constraints. Missing any one of them is usually why prompts underperform.",
            "key_points": [
                "Role: Who should the AI be? Define expertise and perspective",
                "Context: What background does it need to know?",
                "Task: What exactly are you asking it to do?",
                "Format: How should the output be structured?",
                "Constraints: What should it avoid, limit, or always include?",
            ],
        },
        {
            "title": "Zero-Shot vs Few-Shot Prompting",
            "icon": "📊",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "Zero-shot gives instructions only. Few-shot provides examples. Few-shot almost always outperforms zero-shot for complex tasks — 3–5 examples is usually the sweet spot.",
            "key_points": [
                "Zero-shot: instructions only — works for simple, well-defined tasks",
                "One-shot: one example — great for format and tone guidance",
                "Few-shot: 3–5 examples — best for complex or nuanced outputs",
                "Examples should span the range of inputs you expect",
                "Negative examples (what NOT to produce) are also highly effective",
            ],
        },
        {
            "title": "Chain-of-Thought Prompting",
            "icon": "🔗",
            "difficulty": "Intermediate",
            "read_time": "4 min",
            "summary": "Asking the AI to reason step-by-step before answering dramatically improves accuracy on complex reasoning, math, and multi-step analysis tasks.",
            "key_points": [
                "Add \"Think step by step\" for reasoning and analysis tasks",
                "Use \"Reason through this carefully before answering\" for nuanced topics",
                "Chain-of-thought improves accuracy by 20–40% on hard problems",
                "Works best when combined with few-shot examples",
                "Claude, GPT-4, and Gemini all have built-in reasoning capabilities you can activate",
            ],
        },
        {
            "title": "Prompt Iteration Strategies",
            "icon": "🔄",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "The first prompt is rarely the best one. Systematic iteration — not random tweaking — is how professional prompt engineers improve their results.",
            "key_points": [
                "Change one thing at a time to isolate what improves results",
                "Keep a log of what you tried and what worked",
                "Test on edge cases, not just typical inputs",
                "Ask the AI to critique its own output and improve it",
                "Consider prompt quality like you'd consider code quality — it compounds",
            ],
        },
    ],
    "Claude": [
        {
            "title": "Claude Prompt Best Practices",
            "icon": "🟣",
            "difficulty": "Intermediate",
            "read_time": "6 min",
            "summary": "Claude (Anthropic) is optimized for nuanced reasoning, following complex instructions, and long-context tasks. It responds best to structured, explicit, context-rich prompts.",
            "key_points": [
                "Use XML tags to structure sections: <context>, <task>, <format>, <constraints>",
                "Claude respects explicit constraints exceptionally well",
                "Add 'Think carefully before answering' for complex reasoning tasks",
                "Claude handles 200K+ token context windows — use them",
                "Avoid vague instructions — be explicit about every edge case",
            ],
        },
        {
            "title": "XML Structure for Claude",
            "icon": "📐",
            "difficulty": "Advanced",
            "read_time": "5 min",
            "summary": "Claude was trained with XML-tagged prompts and responds measurably better when sections are wrapped in XML. This is the single highest-leverage technique for Claude prompting.",
            "key_points": [
                "<context>: Background information, situation, and existing state",
                "<instructions>: What Claude should do, step by step",
                "<examples>: Input/output pairs demonstrating the format",
                "<output_format>: The exact structure you expect in the response",
                "<constraints>: Hard rules Claude must follow (use NEVER/ALWAYS)",
            ],
        },
        {
            "title": "Claude for Long Documents",
            "icon": "📑",
            "difficulty": "Advanced",
            "read_time": "4 min",
            "summary": "Claude's 200K context window is one of its most powerful features. Here's how to use it effectively for large document analysis and processing.",
            "key_points": [
                "Claude Projects persists context across conversations",
                "Upload files directly rather than pasting content when possible",
                "Instruct Claude to reference specific sections with quotes",
                "For analysis tasks, ask Claude to reason before concluding",
                "Use Claude for cross-document synthesis — it handles multiple files well",
            ],
        },
    ],
    "ChatGPT": [
        {
            "title": "ChatGPT Prompt Best Practices",
            "icon": "🟢",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "ChatGPT responds best to role-playing, step-by-step instructions, and explicit output formats. The system prompt is your most powerful and underused tool.",
            "key_points": [
                "Use system prompts for all persistent instructions and persona",
                "Role injection: 'You are a senior [specific expert with context]...'",
                "Request JSON output for structured data extraction and processing",
                "Ask for reasoning before conclusions on analytical tasks",
                "GPT-4o excels at code generation, analysis, and multimodal tasks",
            ],
        },
        {
            "title": "Custom GPTs and System Prompts",
            "icon": "⚙️",
            "difficulty": "Advanced",
            "read_time": "6 min",
            "summary": "System prompts are where most of the magic happens in ChatGPT. They set the model's behavior, persona, and constraints for the entire conversation.",
            "key_points": [
                "System prompts override default GPT behavior effectively",
                "Define persona, expertise, tone, and output format in system",
                "Include hard constraints as ALWAYS/NEVER rules",
                "Use markdown formatting in system prompts — GPT respects structure",
                "Keep system prompts under 2000 tokens for best results",
            ],
        },
    ],
    "Gemini": [
        {
            "title": "Gemini Prompt Best Practices",
            "icon": "🔵",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "Gemini performs best with grounded, factual contexts and explicit structure. It excels at multimodal tasks and long-context understanding.",
            "key_points": [
                "Provide factual, grounded context — Gemini builds on facts well",
                "Reference specific sources, documents, or data when available",
                "Use step-by-step breakdowns for complex reasoning tasks",
                "Gemini 1.5 Pro handles extremely long contexts (1M+ tokens)",
                "Ask for structured outputs — tables, JSON, numbered lists",
            ],
        },
    ],
    "Research": [
        {
            "title": "Research Prompt Templates",
            "icon": "🔍",
            "difficulty": "Intermediate",
            "read_time": "7 min",
            "summary": "Effective research prompts are built around four pillars: question, scope, methodology, and output format. These patterns work across Perplexity, Claude, and GPT.",
            "key_points": [
                "Define the research question with precision — be specific about what you need",
                "Specify scope: time range, geography, industry, company size",
                "Request citations and source URLs explicitly in every research prompt",
                "Ask for competing perspectives and counterarguments",
                "Structure: executive summary → key findings → evidence → recommendations",
            ],
        },
        {
            "title": "Using Perplexity Effectively",
            "icon": "🔎",
            "difficulty": "Beginner",
            "read_time": "4 min",
            "summary": "Perplexity is optimized for real-time web research with citations. Treat it like a research assistant, not a chatbot.",
            "key_points": [
                "Always request source citations with URLs",
                "Specify recency: 'from the last 6 months only'",
                "Ask Perplexity to compare sources, not just summarize them",
                "Follow up with 'What are the counterarguments?' for balanced research",
                "Use Perplexity for current events, market data, and fact-checking",
            ],
        },
    ],
    "Coding": [
        {
            "title": "Coding Prompt Best Practices",
            "icon": "💻",
            "difficulty": "Intermediate",
            "read_time": "6 min",
            "summary": "Effective coding prompts provide language/framework context, existing code, specific requirements, error messages, and desired output structure — all together.",
            "key_points": [
                "Always specify language, framework, and version explicitly",
                "Include relevant existing code for context — don't ask blindly",
                "Describe the problem you're solving, not just the solution you want",
                "Request error handling, edge cases, and tests",
                "Ask for comments explaining non-obvious logic",
            ],
        },
        {
            "title": "Cursor & Windsurf Agent Best Practices",
            "icon": "⬛",
            "difficulty": "Advanced",
            "read_time": "5 min",
            "summary": "IDE coding agents work best with explicit file references, full task context, and incremental change requests. Vague instructions produce vague code.",
            "key_points": [
                "Reference specific files with @filename or file paths",
                "Describe the full change context, not just the end state",
                "Request one logical change at a time for accuracy",
                "Ask for tests alongside implementations",
                "Use .cursorrules or .windsurfrules for persistent project context",
            ],
        },
        {
            "title": "Building Full-Stack Apps with Lovable & Bolt",
            "icon": "⚡",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "Lovable, Bolt, and Replit Agent respond best to structured app specifications with clear technology choices, user flows, and data models defined upfront.",
            "key_points": [
                "Define your tech stack before starting (e.g., Next.js + Supabase + Tailwind)",
                "Describe user flows as step-by-step user actions",
                "Include data models and relationships explicitly",
                "Specify authentication requirements and user roles",
                "Break complex apps into phases — don't ask for everything at once",
            ],
        },
    ],
    "Product": [
        {
            "title": "Product Management Prompts",
            "icon": "📋",
            "difficulty": "Intermediate",
            "read_time": "6 min",
            "summary": "PM prompts should include: product context, user persona, business constraints, success metrics, and the exact artifact you need (PRD, user story, roadmap, OKR).",
            "key_points": [
                "Define the product, market, and target user with specificity",
                "Include relevant metrics and business context (ARR, MAU, etc.)",
                "Specify the exact artifact: PRD, user story, OKR, roadmap item",
                "Ask for prioritization rationale alongside recommendations",
                "Request both qualitative and quantitative success criteria",
            ],
        },
        {
            "title": "Writing Better PRDs with AI",
            "icon": "📝",
            "difficulty": "Advanced",
            "read_time": "7 min",
            "summary": "AI can generate complete, structured PRDs when given the right context. The key is front-loading all the product context so the AI reasons from your constraints.",
            "key_points": [
                "Include: problem statement, user personas, success metrics, constraints",
                "Provide competitive context and existing solutions",
                "Specify the PRD format (narrative, table, structured sections)",
                "Ask for edge cases and open questions to be listed",
                "Request a prioritized MVP scope alongside the full vision",
            ],
        },
    ],
    "Marketing": [
        {
            "title": "Marketing Prompt Templates",
            "icon": "📣",
            "difficulty": "Beginner",
            "read_time": "5 min",
            "summary": "Marketing prompts need: brand voice definition, specific target audience, channel context, and clear calls-to-action. Tone examples dramatically improve output quality.",
            "key_points": [
                "Define brand voice with 3–5 specific adjectives (e.g., 'confident, direct, human')",
                "Specify target audience with psychographics, not just demographics",
                "Include the channel context (LinkedIn post vs. email vs. landing page)",
                "Provide a tone example: 'Write in a style similar to...'",
                "Always ask for 3+ variants — the first is rarely the best",
            ],
        },
        {
            "title": "Copywriting with AI",
            "icon": "✍️",
            "difficulty": "Intermediate",
            "read_time": "5 min",
            "summary": "Great AI copywriting requires you to front-load the brief — the more specific you are about audience, channel, tone, and CTA, the better the copy.",
            "key_points": [
                "Define the single most important thing you want the reader to feel or do",
                "Specify word/character count for platform constraints",
                "Include the unique value proposition and key differentiators",
                "Ask for hooks/headlines as a separate deliverable",
                "Request A/B variants with different angles or tones",
            ],
        },
    ],
    "Academic": [
        {
            "title": "Academic Research Prompts",
            "icon": "🎓",
            "difficulty": "Advanced",
            "read_time": "7 min",
            "summary": "Academic prompts require precise language, source quality specifications, citation styles, and structured argumentation. Scholarly context transforms output quality.",
            "key_points": [
                "Specify citation style: APA 7, MLA 9, Chicago 17, IEEE",
                "Request peer-reviewed sources — specify if you need primary research",
                "Define the argumentation structure: thesis, evidence, analysis, conclusion",
                "Ask for counterarguments and acknowledged limitations",
                "Specify academic level: undergraduate, graduate, doctoral, journal-quality",
            ],
        },
        {
            "title": "Literature Review Prompts",
            "icon": "📖",
            "difficulty": "Advanced",
            "read_time": "6 min",
            "summary": "AI-assisted literature reviews need clear scope definitions, source quality criteria, and structured output formats to produce citable, useful summaries.",
            "key_points": [
                "Define the research domain and time period explicitly",
                "Specify: seminal works only vs. comprehensive coverage",
                "Request thematic organization, not chronological listing",
                "Ask for identification of research gaps and open questions",
                "Always verify citations independently — AI can hallucinate references",
            ],
        },
    ],
}


def get_contextual_tip(context: str = "always", platform: Optional[str] = None) -> dict:
    """Return a contextually relevant tip."""
    relevant = []

    for tip in TIPS:
        if tip["trigger"] == "always":
            relevant.append((tip, 1))
        if context and tip["trigger"] == context:
            relevant.append((tip, 3))
        if platform and tip.get("platform") == platform:
            relevant.append((tip, 2))

    if not relevant:
        return random.choice(TIPS)

    # Weighted random selection
    pool = []
    for tip, weight in relevant:
        pool.extend([tip] * weight)
    return random.choice(pool)


def get_rotating_tips(count: int = 3) -> list:
    """Return a random selection of tips."""
    return random.sample(TIPS, min(count, len(TIPS)))


def get_empty_state_example() -> str:
    """Return a random example prompt for empty states."""
    return random.choice(EXAMPLE_PROMPTS)
