"""
LLM-powered prompt optimization via Ollama (local, free, private).

Falls back gracefully to None if Ollama is not running or has no models.
"""

from __future__ import annotations

import re
from typing import Optional

SYSTEM_PROMPT = """You are an expert prompt engineer. Your only job is to rewrite the user's prompt to be shorter, sharper, and more structured — while keeping every technical detail and constraint intact.

Follow these rules exactly:

REMOVE without mercy:
- Polite openers: "please", "I would like you to", "I want you to", "could you", "can you"
- Hedging: "I think", "maybe", "perhaps", "I believe", "sort of", "kind of"
- Weak intensifiers: "very", "really", "quite", "extremely", "basically", "actually", "just", "simply"
- Meta-commentary: "it is important to note that", "please note that", "as mentioned above", "note that"
- Filler transitions: "Also,", "Additionally,", "Furthermore,", "On top of that,"
- Verbose phrases: replace "in order to" → "to", "make use of" → "use", "has the ability to" → "can", "make sure to" → (just the verb), "in the event that" → "if"
- Conditional fluff: "it would be nice if you could", "if you can also"

STRUCTURE the output using markdown when the prompt has multiple parts:
**Role:** (only if a role/persona was specified)
**Task:** (one clear imperative sentence — starts with a verb like Build/Create/Implement)
**Stack:** (bullet list of technologies, only real libraries/frameworks — not "REST" or "HTTP")
**Requirements:** (bullet list — each item is a concrete, specific requirement)
**Constraints:** (bullet list — only hard rules like "do not", "must not", "preserve X")

RULES:
- Output ONLY the optimized prompt. No preamble, no explanation, no "Here is the optimized prompt:".
- Preserve ALL technical specifics: library names, version numbers, field names, business logic, data models.
- Never drop a constraint or a "do not / must not" instruction.
- If the prompt is already short and clear (under 100 words), just clean it up — don't over-structure it.
- Use imperative mood: "Build", "Create", "Implement", "Add", not "You should build".
- Each requirement bullet should be specific, not vague ("JWT authentication" not "secure auth").
"""


def _build_user_message(prompt: str) -> str:
    return f"Optimize this prompt:\n\n{prompt}"


def get_available_models() -> list[str]:
    """Return list of locally installed Ollama model names, or [] if unavailable."""
    try:
        import ollama
        models = ollama.list()
        # API returns ModelResponse objects or dicts depending on version
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
                "temperature": 0.3,   # low temp = consistent, focused output
                "num_predict": 1024,  # enough for any prompt
            },
        )
        result: str = response["message"]["content"].strip()

        # Strip any preamble the model added despite instructions
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
    # Also strip trailing meta-commentary
    SUFFIX_RE = re.compile(
        r"^(?:this\s+(?:version|prompt)|i\s+(?:removed|kept|preserved|made))",
        re.IGNORECASE,
    )
    while lines and SUFFIX_RE.match(lines[-1].strip()):
        lines.pop()
    return "\n".join(lines).strip()
