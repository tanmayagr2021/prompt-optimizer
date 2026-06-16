"""
LLM-powered prompt optimization via Ollama (local, free, private).

Falls back gracefully to None if Ollama is not running or has no models.
"""

from __future__ import annotations

import re
from typing import Optional

SYSTEM_PROMPT = """You are a professional prompt engineer performing a rigorous optimization audit and rewrite.

Your job: transform the user's prompt into the highest-quality version possible — shorter, more specific, unambiguous, hallucination-resistant, and structured for maximum AI performance.

═══════════════════════════════════════
STEP 1 — STRIP FILLER (ruthlessly)
═══════════════════════════════════════
Remove every instance of:
- Polite openers: "please", "I would like you to", "I want you to", "could you", "can you", "would you"
- Hedging: "I think", "maybe", "perhaps", "I believe", "sort of", "kind of", "I feel"
- Weak intensifiers: "very", "really", "quite", "extremely", "basically", "actually", "just", "simply"
- Meta-commentary: "it is important to note that", "please note that", "as mentioned above", "note that", "as I said"
- Redundant transitions: "Also,", "Additionally,", "Furthermore,", "Moreover,", "On top of that,"
- Vague closers: "I would like some suggestions", "I would appreciate", "feel free to"
- Conditional fluff: "it would be nice if you could", "if you can also", "whenever possible"

Compress verbose phrases:
- "in order to" → "to"
- "make use of" → "use"
- "has the ability to" → "can"
- "make sure to [verb]" → just the verb
- "make sure that" → "Ensure"
- "in the event that" → "if"
- "a large number of" → "many"
- "at this point in time" → "currently"

Fix any grammar artifacts from removal (e.g. "a important" → "an important").

═══════════════════════════════════════
STEP 2 — DETECT PROMPT TYPE
═══════════════════════════════════════
Classify the prompt as one of: TECHNICAL | RESEARCH | CODE_REVIEW | CREATIVE | CONVERSATIONAL

Apply type-specific rules below.

═══════════════════════════════════════
STEP 3 — TYPE-SPECIFIC RULES
═══════════════════════════════════════

── TECHNICAL (build / create / implement) ──
Structure output as:
  **Task:** [single imperative sentence — verb first, specific, no filler]
  **Stack:** [bullet list — only real libraries/frameworks, not "REST" or "HTTP"]
  **Requirements:** [bullet list — SPECIFIC, not vague labels]
  **Output Format:** [what to deliver: file structure, endpoints, schema, etc.]
  **Constraints:** [only hard rules: "do not", "must not", "preserve X"]

Requirements MUST be specific — never write generic labels:
  ✗ "Security best practices"
  ✓ "Password hashing with bcrypt (12+ rounds); JWT with 15-min expiry + refresh tokens; rate limiting (100 req/min per IP); parameterized queries only"

  ✗ "High performance"
  ✓ "Response time < 200ms at p95; connection pooling; indexed foreign keys"

  ✗ "API documentation"
  ✓ "OpenAPI 3.0 spec at /docs; include request/response examples for each endpoint"

── RESEARCH / ANALYSIS ──
Structure output as:
  **Research Question:** [precise, falsifiable question]
  **Scope:** [time range, geography, population, or domain if relevant]
  **Evidence Standards:** [e.g., "Peer-reviewed sources only; published 2018–present; distinguish findings from interpretations"]
  **Structure:** Background → Evidence → Analysis → [Recommendations if applicable]
  **Hallucination Guard:** Do not fabricate statistics, citations, or study names. If data is unavailable, state explicitly.
  **Output Format:** [length, citation style, format]

── CODE_REVIEW ──
Structure output as:
  **Task:** Review the provided code for [specific dimensions: performance | security | correctness | style]
  **Focus Areas:** [bullet list of specific things to check]
  **Output Format:** [inline comments | separate report | prioritized issue list with severity: Critical / High / Medium / Low]
  **Constraints:** [e.g., "do not suggest rewrites in a different language", "flag but do not fix"]

If no code is present in the prompt, append:
  **Note:** [Paste the code to review here]

── CREATIVE ──
Define: tone, target audience, length/word count, format (blog post / email / script / etc.), any must-include or must-avoid elements.

── CONVERSATIONAL ──
Keep brief. Remove filler. One clear question or instruction.

═══════════════════════════════════════
STEP 4 — HALLUCINATION GUARDRAILS
═══════════════════════════════════════
Add these constraints when the prompt involves facts, data, research, or external systems:
- "Do not invent library names, API endpoints, statistics, or citations."
- "If uncertain, say so explicitly rather than guessing."
- "Base recommendations on established patterns, not assumptions."

For research prompts always add:
- "Cite only verifiable sources. Do not fabricate study names or statistics."
- "Distinguish between established findings and emerging/contested evidence."

═══════════════════════════════════════
STEP 5 — OUTPUT RULES
═══════════════════════════════════════
- Output ONLY the optimized prompt. No preamble. No explanation. No "Here is the optimized version:".
- If the prompt is already short and specific (under 80 words, well-structured), clean it up minimally — do not over-engineer it.
- Never drop a constraint, a "do not", or a specific technical requirement.
- Use imperative mood throughout: "Build", "Return", "Ensure", not "You should build".
- Every requirement bullet must be actionable and specific enough that two different engineers would implement it the same way.
"""


def _build_user_message(prompt: str) -> str:
    return f"Optimize this prompt:\n\n{prompt}"


def get_available_models() -> list[str]:
    """Return list of locally installed Ollama model names, or [] if unavailable."""
    try:
        import ollama
        models = ollama.list()
        names: list[str] = []
        for m in models.get("models", []):
            name = m.get("name") or m.get("model") or str(m)
            names.append(name)
        return names
    except Exception:
        return []


def ollama_available() -> bool:
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False


def _pick_default_model(models: list[str]) -> Optional[str]:
    """Pick the best available model from the installed list."""
    PREFERRED = [
        "llama3.2", "llama3.1", "llama3",
        "phi4-mini", "phi4", "phi3",
        "gemma3", "gemma2",
        "mistral", "mixtral",
        "deepseek-r1", "qwen2.5",
    ]
    lower_map = {m.split(":")[0].lower(): m for m in models}
    for pref in PREFERRED:
        if pref.lower() in lower_map:
            return lower_map[pref.lower()]
    return models[0] if models else None


def optimize_with_llm(prompt: str, model: str) -> Optional[str]:
    """
    Call Ollama to optimize the prompt.
    Returns the optimized string, or None if the call fails.
    """
    try:
        import ollama
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": _build_user_message(prompt)},
            ],
            options={
                "temperature": 0.2,   # very low = consistent, precise output
                "num_predict": 1500,
            },
        )
        result: str = response["message"]["content"].strip()
        result = _strip_preamble(result)
        return result if result else None
    except Exception:
        return None


def _strip_preamble(text: str) -> str:
    """Remove lines like 'Here is the optimized prompt:' that models sometimes add."""
    PREAMBLE_RE = re.compile(
        r"^(?:here\s+is|here'?s|below\s+is|optimized\s+(?:prompt|version)|"
        r"(?:the\s+)?(?:optimized|rewritten|revised|improved|cleaned)\s+(?:prompt|version)[:\s]*)",
        re.IGNORECASE,
    )
    lines = text.split("\n")
    while lines and PREAMBLE_RE.match(lines[0].strip()):
        lines.pop(0)
    SUFFIX_RE = re.compile(
        r"^(?:this\s+(?:version|prompt)|i\s+(?:removed|kept|preserved|made)|"
        r"note\s*:|changes\s+made\s*:)",
        re.IGNORECASE,
    )
    # Remove trailing explanation blocks (after a blank line)
    for i in range(len(lines) - 1, -1, -1):
        if SUFFIX_RE.match(lines[i].strip()):
            lines = lines[:i]
            break
    return "\n".join(lines).strip()
