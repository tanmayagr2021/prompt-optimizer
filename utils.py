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
