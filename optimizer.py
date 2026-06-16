"""
Core optimization pipeline.

Automatically selects the right strategy based on prompt size and structure:
  small  (<500 chars)  → light cleanup + minor enhancement
  medium (500-3k chars) → cleanup + redundancy removal + selective restructuring
  large  (>3k chars)   → full spec generation
"""

import re
from typing import Dict, List, Optional, Tuple

from analyzer import IntentAnalyzer
from utils import clean_whitespace, split_paragraphs, is_well_structured


# ---------------------------------------------------------------------------
# Phrase enhancement map (only high-confidence, unambiguous substitutions)
# ---------------------------------------------------------------------------
ENHANCEMENT_MAP: List[Tuple[str, str]] = [
    (r"\bmake\s+a\s+website\b", "Build a production-ready website"),
    (r"\bcreate\s+a\s+website\b", "Build a production-ready website"),
    (r"\bmake\s+a\s+web\s+app\b", "Build a production-ready web application"),
    (r"\bcreate\s+a\s+web\s+app\b", "Build a production-ready web application"),
    (r"\bmake\s+a\s+dashboard\b", "Build a responsive dashboard application"),
    (r"\bcreate\s+a\s+dashboard\b", "Build a responsive dashboard application"),
    (r"\bmake\s+an?\s+API\b", "Build a production-ready REST API"),
    (r"\bcreate\s+an?\s+API\b", "Build a production-ready REST API"),
]

# Redundancy groups — phrases that mean the same thing
REDUNDANCY_GROUPS: List[List[str]] = [
    ["responsive design", "mobile friendly", "mobile-friendly", "mobile responsive",
     "works on mobile", "works on phones", "supports small screens", "mobile support",
     "optimized for mobile", "mobile-first"],
    ["production ready", "production-ready", "production grade", "production-grade",
     "ready for production"],
    ["user friendly", "user-friendly", "easy to use", "intuitive interface",
     "simple to use", "easy-to-use"],
    ["secure", "security", "secure coding", "follow security best practices",
     "implement security"],
    ["performance", "fast", "performant", "high performance", "optimized performance",
     "fast loading", "quick"],
    ["scalable", "scalability", "scales well", "horizontally scalable",
     "designed to scale"],
    ["clean code", "readable code", "well-written code", "maintainable code",
     "good code quality", "code quality"],
]

# Role prose patterns to strip after role is extracted
ROLE_PROSE_PATTERNS: List[str] = [
    r"I\s+want\s+you\s+to\s+act\s+as\s+[^\n.]+[.\n]?",
    r"You\s+are\s+(?:a\s+|an\s+)?[^\n.]+(?:engineer|developer|expert|specialist)[^\n.]*[.\n]?",
    r"Act\s+as\s+(?:a\s+|an\s+)?[^\n.]+[.\n]?",
    r"Your\s+role\s+is\s+[^\n.]+[.\n]?",
    r"As\s+(?:a\s+|an\s+)?(?:experienced|senior|expert|skilled)\s+[^\n.]+,\s*",
]


class PromptOptimizer:
    """Main optimizer — call .optimize(text) to run the full pipeline."""

    def __init__(self) -> None:
        self.analyzer = IntentAnalyzer()
        self._encoder = None
        self._encoder_loaded = False

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def optimize(self, text: str) -> Dict:
        """
        Run the full optimization pipeline and return a result dict:
          {
            "optimized": str,
            "intent":    dict,
            "mode":      "small" | "medium" | "large",
          }
        """
        intent = self.analyzer.analyze(text)
        size = self._effective_size(intent, text)

        # Step 1: cleanup
        cleaned = self._cleanup(text)

        # Step 2: extract constraints BEFORE any removal (to protect them)
        protected = intent["constraints"]

        # Step 3: remove redundancy
        deduped = self._remove_redundancy(cleaned)

        # Step 4 & 5: structure + enhance
        if size == "large":
            optimized = self._generate_spec(deduped, intent)
        elif size == "medium":
            optimized = self._medium_optimize(deduped, intent)
        else:
            optimized = self._light_optimize(deduped)

        # Step 6: guarantee constraints survived
        optimized = self._ensure_constraints(optimized, protected)

        return {"optimized": optimized, "intent": intent, "mode": size}

    def _effective_size(self, intent: Dict, text: str) -> str:
        """
        Determine effective optimization mode.
        Document-type documents (PRDs, specs, meeting notes) get spec generation
        at 1500+ chars; plain prompts need 3000+ chars to trigger it.
        """
        raw_size = intent["prompt_size"]
        if raw_size == "small":
            return "small"
        doc_type = intent.get("doc_type", "general")
        char_count = len(text)
        if doc_type in ("prd", "spec", "meeting", "business") and char_count >= 1_500:
            return "large"
        if char_count >= 3_000:
            return "large"
        return "medium"

    # ------------------------------------------------------------------
    # Step 1: Cleanup
    # ------------------------------------------------------------------

    def _cleanup(self, text: str) -> str:
        # Strip HTML tags
        text = re.sub(r"<[^>]+>", " ", text)
        # Normalize entities
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&nbsp;", " ").replace("&#x27;", "'")

        # Remove decorative markdown (horizontal rules, excessive asterisks)
        text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*{3,}", "", text)
        text = re.sub(r"_{3,}", "", text)

        # Normalize headers deeper than ### → ###
        text = re.sub(r"^#{4,}\s*", "### ", text, flags=re.MULTILINE)

        # Remove trailing colon-only lines (e.g. "Requirements:" followed immediately
        # by another header — the colon version adds no value in those cases)
        # We keep them when they precede content.

        # Normalize whitespace
        text = clean_whitespace(text)

        # Remove exact-duplicate lines
        text = self._dedup_lines(text)

        return text

    def _dedup_lines(self, text: str) -> str:
        seen: set[str] = set()
        result: list[str] = []
        for line in text.split("\n"):
            key = line.strip().lower()
            if not key or key not in seen:
                result.append(line)
            if key:
                seen.add(key)
        return "\n".join(result)

    # ------------------------------------------------------------------
    # Step 2: Redundancy removal
    # ------------------------------------------------------------------

    def _remove_redundancy(self, text: str) -> str:
        # Pass A: paragraph-level dedup (across \n\n-separated blocks)
        paragraphs = split_paragraphs(text)
        if len(paragraphs) > 1:
            encoder = self._get_encoder()
            if encoder and len(paragraphs) > 3:
                paragraphs = self._semantic_dedup(paragraphs, encoder)
            else:
                paragraphs = self._phrase_dedup_paragraphs(paragraphs)

        # Pass B: bullet-level dedup within each paragraph/section
        paragraphs = [self._dedup_bullets_in_block(p) for p in paragraphs]

        return "\n\n".join(p for p in paragraphs if p.strip())

    def _semantic_dedup(self, paragraphs: List[str], encoder) -> List[str]:
        try:
            import numpy as np

            # Only consider paragraphs with real content (skip short headers)
            indexed = [(i, p) for i, p in enumerate(paragraphs) if len(p) > 40]
            if len(indexed) < 2:
                return paragraphs

            idxs, texts = zip(*indexed)
            embeddings = encoder.encode(list(texts), show_progress_bar=False)

            # Cosine similarity without sklearn
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
            normed = embeddings / (norms + 1e-10)
            sim = normed @ normed.T

            to_remove: set[int] = set()
            for i in range(len(texts)):
                if i in to_remove:
                    continue
                for j in range(i + 1, len(texts)):
                    if j in to_remove:
                        continue
                    if sim[i, j] > 0.85:
                        # Keep the longer / more informative paragraph
                        keep, drop = (i, j) if len(texts[i]) >= len(texts[j]) else (j, i)
                        to_remove.add(drop)

            kept_positions = {idxs[i] for i in range(len(idxs)) if i not in to_remove}

            return [
                p for pos, p in enumerate(paragraphs)
                if len(p) <= 40 or pos in kept_positions
            ]
        except Exception:
            return self._phrase_dedup_paragraphs(paragraphs)

    def _phrase_dedup_paragraphs(self, paragraphs: List[str]) -> List[str]:
        """Remove entire paragraphs that belong to an already-seen redundancy group."""
        used_groups: set[int] = set()
        result: list[str] = []
        for para in paragraphs:
            para_lower = para.lower()
            should_drop = False
            for group_id, group in enumerate(REDUNDANCY_GROUPS):
                if any(phrase in para_lower for phrase in group):
                    if group_id in used_groups:
                        should_drop = True
                    else:
                        used_groups.add(group_id)
                    break
            if not should_drop:
                result.append(para)
        return result

    def _dedup_bullets_in_block(self, text: str) -> str:
        """Remove redundant bullet lines within a single block of text."""
        lines = text.split("\n")
        used_groups: set[int] = set()
        to_remove: set[int] = set()

        for line_idx, line in enumerate(lines):
            stripped = line.strip()
            # Only process actual bullet lines
            if not re.match(r"^[-*•]\s+", stripped):
                continue
            line_lower = stripped.lower()
            for group_id, group in enumerate(REDUNDANCY_GROUPS):
                if any(phrase in line_lower for phrase in group):
                    if group_id in used_groups:
                        to_remove.add(line_idx)
                    else:
                        used_groups.add(group_id)
                    break

        return "\n".join(l for i, l in enumerate(lines) if i not in to_remove)

    # ------------------------------------------------------------------
    # Step 3a: Light optimization (small prompts)
    # ------------------------------------------------------------------

    def _light_optimize(self, text: str) -> str:
        text = self._apply_enhancements(text)
        return text

    # ------------------------------------------------------------------
    # Step 3b: Medium optimization
    # ------------------------------------------------------------------

    def _medium_optimize(self, text: str, intent: Dict) -> str:
        parts: list[str] = []
        remaining = text

        # Extract role if found in prose
        role = intent.get("role")
        if role and not intent.get("already_structured"):
            remaining = self._strip_role_prose(remaining)
            parts.append(f"**Role:** {role.strip().rstrip('.,:')}")

        # Extract tech stack if mentioned inline
        tech = intent.get("tech_stack", [])
        if tech and len(tech) >= 2 and not intent.get("already_structured"):
            remaining = self._strip_tech_prose(remaining, tech)
            stack_lines = "\n".join(f"- {t}" for t in tech)
            parts.append(f"**Stack:**\n{stack_lines}")

        # Enhance remaining text
        remaining = self._apply_enhancements(remaining.strip())
        remaining = self._prose_to_bullets(remaining)

        if parts:
            return "\n\n".join(parts) + "\n\n" + remaining
        return remaining

    def _strip_role_prose(self, text: str) -> str:
        for pattern in ROLE_PROSE_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return clean_whitespace(text)

    def _strip_tech_prose(self, text: str, tech_stack: List[str]) -> str:
        """Remove inline tech stack sentences when we've extracted them."""
        patterns = [
            r"(?:use|using|with|built with|powered by|stack:?)\s+"
            + r"(?:" + "|".join(re.escape(t) for t in tech_stack) + r")"
            + r"(?:[^\n.]{0,80})?",
        ]
        for pattern in patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return clean_whitespace(text)

    def _apply_enhancements(self, text: str) -> str:
        for pattern, replacement in ENHANCEMENT_MAP:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _prose_to_bullets(self, text: str) -> str:
        """Convert comma-separated lists within a sentence to bullet points."""
        def convert_list_sentence(m: re.Match) -> str:
            intro = m.group(1)
            items_raw = m.group(2)
            items = [i.strip() for i in re.split(r",\s*(?:and\s+|or\s+)?", items_raw) if i.strip()]
            if len(items) < 3:
                return m.group(0)
            bullets = "\n".join(f"- {item}" for item in items)
            return f"{intro}:\n{bullets}"

        text = re.sub(
            r"((?:include|support|using|use|require|need)[s]?)\s+([a-zA-Z][^.:\n]{20,120}(?:,\s*(?:and\s+)?[a-zA-Z][^,.\n]+){2,})",
            convert_list_sentence,
            text,
            flags=re.IGNORECASE,
        )
        return text

    # ------------------------------------------------------------------
    # Step 3c: Spec generation (large prompts)
    # ------------------------------------------------------------------

    def _generate_spec(self, text: str, intent: Dict) -> str:
        """Convert a large document into a structured Claude Code spec."""
        sections: Dict[str, str] = {}

        # Objective — single sentence only
        obj = intent.get("objective") or self._first_meaningful_sentence(text)
        if obj:
            # Trim to first sentence if multi-sentence
            first_sentence = re.split(r"(?<=[.!?])\s+", obj)[0]
            sections["# Objective"] = first_sentence.strip().rstrip(".")

        # Users / Roles
        users = intent.get("users", [])
        if users:
            sections["# Users"] = "\n".join(f"- {u}" for u in users)

        # Features — prefer bullets from a "features / requirements" section
        features = self._extract_features_scoped(text, intent)
        if features:
            sections["# Features"] = "\n".join(f"- {f}" for f in features[:20])

        # Tech Stack (filter out generic terms like REST, CSS)
        tech = [t for t in intent.get("tech_stack", []) if t not in ("REST", "CSS")]
        if tech:
            sections["# Tech Stack"] = "\n".join(f"- {t}" for t in tech)

        # Constraints — deduplicated
        constraints = self._dedup_constraints(intent.get("constraints", []))
        if constraints:
            sections["# Constraints"] = "\n".join(f"- {c}" for c in constraints[:10])

        # Deliverables
        deliverables = intent.get("deliverables", [])
        if deliverables:
            sections["# Deliverables"] = "\n".join(f"- {d}" for d in deliverables[:6])

        if len(sections) < 2:
            return self._medium_optimize(text, intent)

        return "\n\n".join(f"{header}\n\n{body}" for header, body in sections.items())

    def _first_meaningful_sentence(self, text: str) -> Optional[str]:
        """Return the first sentence that contains a meaningful verb."""
        clean = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        for s in sentences[:6]:
            s = s.strip()
            if len(s) > 20 and re.search(
                r"\b(?:build|create|develop|design|implement|manage|track|provide)\b",
                s, re.IGNORECASE
            ):
                return s
        # Fallback: first line with enough content
        for line in text.split("\n"):
            line = re.sub(r"^#+\s*", "", line).strip()
            if len(line) > 25:
                return line
        return None

    def _extract_features_scoped(self, text: str, intent: Dict) -> List[str]:
        """
        Extract features preferring content under feature/requirement section headers.
        Excludes constraint-like and deliverable-like bullets.
        """
        CONSTRAINT_RE = re.compile(
            r"^(?:do not|don't|must not|never|avoid|preserve|maintain|keep|"
            r"do not modify|must not use|all data)",
            re.IGNORECASE,
        )
        DELIVERABLE_RE = re.compile(
            r"^(?:complete source|source code|deployment guide|api doc|"
            r"database schema|test suite|user doc|admin guide|unit test)",
            re.IGNORECASE,
        )

        features: list[str] = []

        # Locate a features/requirements section in the text
        section_re = re.compile(
            r"^(?:#{1,3}\s*)?(?:core\s+)?(?:features?|requirements?|functionality|capabilities)[^\n]*$",
            re.IGNORECASE | re.MULTILINE,
        )
        m = section_re.search(text)
        if m:
            # Take up to 800 chars after the header, stop at next header
            section_text = text[m.end(): m.end() + 800]
            next_header = re.search(r"^#{1,3}\s+\w", section_text, re.MULTILINE)
            if next_header:
                section_text = section_text[: next_header.start()]
            bullets = re.findall(r"^[-*•]\s+(.+)$", section_text, re.MULTILINE)
            for b in bullets:
                b = b.strip()
                if 5 < len(b) < 120 and not CONSTRAINT_RE.match(b) and not DELIVERABLE_RE.match(b):
                    features.append(b)

        # Fallback: all bullets not matching constraint/deliverable patterns
        if not features:
            all_bullets = re.findall(r"^[-*•]\s+(.+)$", text, re.MULTILINE)
            for b in all_bullets:
                b = b.strip()
                if 5 < len(b) < 120 and not CONSTRAINT_RE.match(b) and not DELIVERABLE_RE.match(b):
                    features.append(b)

        # Also check intent's pre-extracted features as supplement
        for f in intent.get("features", []):
            if not CONSTRAINT_RE.match(f) and not DELIVERABLE_RE.match(f):
                features.append(f)

        # Deduplicate
        seen: set[str] = set()
        unique: list[str] = []
        for f in features:
            key = f.lower()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _dedup_constraints(self, constraints: List[str]) -> List[str]:
        """Remove near-duplicate constraints (same first 40 chars)."""
        seen: set[str] = set()
        unique: list[str] = []
        for c in constraints:
            key = re.sub(r"\s+", " ", c.lower().strip())[:40]
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique

    # ------------------------------------------------------------------
    # Step 4: Constraint enforcement
    # ------------------------------------------------------------------

    def _ensure_constraints(self, optimized: str, constraints: List[str]) -> str:
        """Re-inject any constraints that were lost during optimization."""
        if not constraints:
            return optimized

        missing: list[str] = []
        for c in constraints:
            # Match on the first 60 chars of the constraint text
            needle = re.escape(c[:60].lower())
            if not re.search(needle, optimized.lower()):
                missing.append(c)

        if missing:
            block = "\n".join(f"- {c}" for c in missing)
            optimized = optimized.rstrip() + f"\n\n**Constraints:**\n{block}"

        return optimized

    # ------------------------------------------------------------------
    # Sentence-transformers lazy loader
    # ------------------------------------------------------------------

    def _get_encoder(self):
        if self._encoder_loaded:
            return self._encoder
        self._encoder_loaded = True
        try:
            from sentence_transformers import SentenceTransformer
            self._encoder = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception:
            self._encoder = None
        return self._encoder
