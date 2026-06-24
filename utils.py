"""Utility functions for statistics, token estimation, and text helpers."""

import re
from typing import Dict


def estimate_tokens(text: str) -> int:
    """Estimate token count using the 4-chars-per-token approximation."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def calculate_stats(original: str, optimized: str) -> Dict:
    """Return before/after character and token statistics."""
    orig_chars = len(original)
    opt_chars = len(optimized)
    chars_removed = orig_chars - opt_chars
    reduction_pct = (chars_removed / orig_chars * 100) if orig_chars > 0 else 0.0

    orig_tokens = estimate_tokens(original)
    opt_tokens = estimate_tokens(optimized)
    token_reduction = orig_tokens - opt_tokens
    token_reduction_pct = (token_reduction / orig_tokens * 100) if orig_tokens > 0 else 0.0

    return {
        "original_chars": orig_chars,
        "optimized_chars": opt_chars,
        "chars_removed": chars_removed,
        "reduction_pct": round(reduction_pct, 1),
        "original_tokens": orig_tokens,
        "optimized_tokens": opt_tokens,
        "token_reduction": token_reduction,
        "token_reduction_pct": round(token_reduction_pct, 1),
    }


def clean_whitespace(text: str) -> str:
    """Normalize whitespace while preserving paragraph structure."""
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    """Split text into non-empty paragraphs."""
    return [p.strip() for p in re.split(r"\n\n+", text) if p.strip()]


def count_words(text: str) -> int:
    return len(text.split())


def is_well_structured(text: str) -> bool:
    """Return True if the text already uses markdown headers or bullet lists."""
    has_headers = bool(re.search(r"^#{1,3}\s+\w", text, re.MULTILINE))
    has_bullets = bool(re.search(r"^[-*•]\s+\w", text, re.MULTILINE))
    return has_headers or has_bullets


def analyze_changes(original: str, optimized: str) -> list:
    """Compare original and optimized prompts and return categorized insights."""
    insights = []

    # Structure: headers added
    orig_headers = len(re.findall(r"^#{1,3}\s", original, re.MULTILINE))
    opt_headers = len(re.findall(r"^#{1,3}\s", optimized, re.MULTILINE))
    if opt_headers > orig_headers:
        insights.append({
            "category": "Structure",
            "icon": "🏗️",
            "color": "indigo",
            "change": f"Added {opt_headers - orig_headers} section header(s)",
            "why": "Headers help the model parse and organize its response into logical sections",
        })

    # Clarity: bullets added
    orig_bullets = len(re.findall(r"^[-*•]\s", original, re.MULTILINE))
    opt_bullets = len(re.findall(r"^[-*•]\s", optimized, re.MULTILINE))
    if opt_bullets > orig_bullets:
        insights.append({
            "category": "Clarity",
            "icon": "✨",
            "color": "blue",
            "change": f"Converted prose to bullet points (+{opt_bullets - orig_bullets})",
            "why": "Bullet points are easier for AI to parse and produce more consistent structured output",
        })

    # Constraints: explicit constraint words
    constraint_words = ["never", "always", "must", "only", "do not", "don't", "avoid", "ensure", "require", "strictly"]
    orig_c = sum(1 for w in constraint_words if w.lower() in original.lower())
    opt_c = sum(1 for w in constraint_words if w.lower() in optimized.lower())
    if opt_c > orig_c:
        insights.append({
            "category": "Constraints",
            "icon": "🎯",
            "color": "green",
            "change": "Added explicit constraints",
            "why": "Clear constraints reduce hallucination and improve response consistency",
        })

    # XML structure (Claude)
    xml_tags = ["<context>", "<instructions>", "<task>", "<output_format>", "<constraints>", "<examples>"]
    has_xml = any(tag in optimized for tag in xml_tags)
    had_xml = any(tag in original for tag in xml_tags)
    if has_xml and not had_xml:
        insights.append({
            "category": "Format",
            "icon": "📐",
            "color": "purple",
            "change": "Added XML section structure",
            "why": "XML tags help Claude parse sections and follow instructions with significantly higher precision",
        })

    # Role injection
    role_patterns = ["you are", "act as", "you're a", "as a senior", "as an expert"]
    has_role_opt = any(p in optimized.lower()[:300] for p in role_patterns)
    has_role_orig = any(p in original.lower()[:300] for p in role_patterns)
    if has_role_opt and not has_role_orig:
        insights.append({
            "category": "Context",
            "icon": "🎭",
            "color": "orange",
            "change": "Added role/persona injection",
            "why": "Defining who the AI should be significantly improves expertise depth and response quality",
        })

    # Token efficiency
    if len(optimized) < len(original) * 0.88:
        reduction = int((1 - len(optimized) / len(original)) * 100)
        insights.append({
            "category": "Efficiency",
            "icon": "⚡",
            "color": "yellow",
            "change": f"Removed ~{reduction}% token overhead",
            "why": "Leaner prompts reduce cost and often improve focus by eliminating noise",
        })

    # Output format specification
    format_words = ["respond in", "format your", "structure your", "output as", "return a", "provide a", "use the following format"]
    has_fmt_opt = any(p in optimized.lower() for p in format_words)
    has_fmt_orig = any(p in original.lower() for p in format_words)
    if has_fmt_opt and not has_fmt_orig:
        insights.append({
            "category": "Specificity",
            "icon": "📋",
            "color": "teal",
            "change": "Added explicit output format specification",
            "why": "Specifying the exact output format produces consistent, predictable results",
        })

    return insights
