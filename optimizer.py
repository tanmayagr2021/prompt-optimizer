"""
Core optimization pipeline.

Automatically selects the right strategy based on prompt size and structure:
  small  (<500 chars)  → filler removal + enhancement
  medium (500-3k chars) → structured rewrite (Task / Stack / Requirements / Constraints)
  large  (>3k chars)   → full spec generation
"""

import re
from typing import Dict, List, Optional, Tuple

from analyzer import IntentAnalyzer
from utils import clean_whitespace, split_paragraphs


# ---------------------------------------------------------------------------
# Filler phrases — strip entirely or replace with concise equivalent
# ---------------------------------------------------------------------------
FILLER_PHRASES: List[Tuple[str, str]] = [
    # Polite openers
    (r"\bI\s+would\s+like\s+you\s+to\b\s*", ""),
    (r"\bI\s+want\s+you\s+to\b\s*", ""),
    (r"\bI\s+need\s+you\s+to\b\s*", ""),
    (r"\bcould\s+you\s+(?:please\s+)?", ""),
    (r"\bcan\s+you\s+(?:please\s+)?", ""),
    (r"\bwould\s+you\s+(?:please\s+)?", ""),
    (r"\bplease\s+", ""),
    # Meta-commentary
    (r"\bIt\s+is\s+(?:very\s+)?important\s+(?:to\s+note\s+)?that\b\s*", ""),
    (r"\bPlease\s+note\s+that\b\s*", "Note: "),
    (r"\bNote\s+that\b\s*", "Note: "),
    (r"\bAs\s+(?:mentioned|stated|noted|discussed)\s+(?:above|before|previously|earlier)\b[,\s]*", ""),
    (r"\bAs\s+I\s+(?:mentioned|said|noted)\b[,\s]*", ""),
    (r"\bJust\s+to\s+(?:clarify|confirm|recap)\b[,\s]*", ""),
    # Hedging
    (r"\bI\s+think\b[,\s]*", ""),
    (r"\bI\s+believe\b[,\s]*", ""),
    (r"\bI\s+feel\b[,\s]*", ""),
    (r"\bmaybe\b\s*", ""),
    (r"\bperhaps\b\s*", ""),
    (r"\bkind\s+of\b\s*", ""),
    (r"\bsort\s+of\b\s*", ""),
    (r"\bsomewhat\b\s*", ""),
    # Weak intensifiers (safe to drop)
    (r"\bvery\s+(?=\w)", ""),
    (r"\bextremely\s+(?=\w)", ""),
    (r"\breally\s+(?=\w)", ""),
    (r"\bquite\s+(?=\w)", ""),
    (r"\bbasically\b[,\s]*", ""),
    (r"\bactually\b[,\s]*", ""),
    (r"\bsimply\b\s*", ""),
    (r"\bjust\s+(?=(?:make|create|build|add|use|ensure|include|implement|write)\b)", ""),
    # Conditional suggestions ("it would be nice if you could X" → "X")
    (r"\bIt\s+would\s+(?:also\s+)?(?:be\s+)?(?:really\s+|very\s+)?(?:nice|great|good|helpful|ideal)\s+(?:if\s+)?(?:you\s+could\s+)?(?:also\s+)?", ""),
    (r"\bif\s+(?:you\s+)?(?:could|can)\s+(?:also\s+)?", ""),
    # "Make sure it/they/the X has/have" → ""  (not followed by "to" — handled above)
    (r"\bmake\s+sure\s+(?:that\s+)?(?:it|they|the\s+\w+)\s+", "Ensure it "),
    # Also/additionally fluff
    (r"\bAlso\s+(?:please\s+)?", ""),
    (r"\bAdditionally\s*,?\s*(?:please\s+)?", ""),
    (r"\bFurthermore\s*,?\s*", ""),
    (r"\bMoreover\s*,?\s*", ""),
    (r"\bOn\s+top\s+of\s+that\s*,?\s*", ""),
]

# ---------------------------------------------------------------------------
# Verbose → concise phrase compression
# ---------------------------------------------------------------------------
VERBOSE_MAP: List[Tuple[str, str]] = [
    (r"\bin\s+order\s+to\b", "to"),
    (r"\bdue\s+to\s+the\s+fact\s+that\b", "because"),
    (r"\bat\s+this\s+point\s+in\s+time\b", "now"),
    (r"\bin\s+the\s+event\s+that\b", "if"),
    (r"\bfor\s+the\s+purpose\s+of\b", "for"),
    (r"\bwith\s+(?:the\s+)?(?:regard|respect)\s+to\b", "regarding"),
    (r"\bin\s+(?:the\s+)?(?:regard|respect)\s+to\b", "regarding"),
    (r"\bprior\s+to\b", "before"),
    (r"\bsubsequent\s+to\b", "after"),
    (r"\ba\s+(?:large|great|significant)\s+(?:number|amount)\s+of\b", "many"),
    (r"\bthe\s+(?:vast\s+)?majority\s+of\b", "most"),
    (r"\bat\s+the\s+(?:current|present)\s+(?:time|moment)\b", "currently"),
    (r"\bhas\s+the\s+ability\s+to\b", "can"),
    (r"\bis\s+able\s+to\b", "can"),
    (r"\bin\s+(?:a|the)\s+(?:timely|prompt)\s+manner\b", "promptly"),
    (r"\bmake\s+use\s+of\b", "use"),
    (r"\btake\s+into\s+(?:account|consideration)\b", "consider"),
    (r"\bwith\s+the\s+(?:aim|goal|objective|purpose)\s+of\b", "to"),
    (r"\bfor\s+the\s+(?:reason|purpose)\s+that\b", "because"),
    (r"\bin\s+(?:a|an)\s+efficient\s+(?:way|manner)\b", "efficiently"),
    (r"\bin\s+(?:a|an)\s+effective\s+(?:way|manner)\b", "effectively"),
    (r"\bprovide\s+(?:the\s+)?(?:ability|capability)\s+to\b", "support"),
    (r"\ballow\s+(?:the\s+)?(?:user|users)\s+to\b", "let users"),
    (r"\ballow\s+(?:the\s+)?(?:admin|admins)\s+to\b", "let admins"),
    (r"\bmake\s+sure\s+to\s+", ""),
    (r"\bmake\s+sure\s+that\s+", "Ensure "),
    (r"\bensure\s+that\s+(?:you\s+)?", "ensure "),
]

# ---------------------------------------------------------------------------
# Phrase enhancement (vague → specific)
# ---------------------------------------------------------------------------
ENHANCEMENT_MAP: List[Tuple[str, str]] = [
    (r"\bmake\s+a\s+website\b", "Build a production-ready website"),
    (r"\bcreate\s+a\s+website\b", "Build a production-ready website"),
    (r"\bmake\s+a\s+web\s+app\b", "Build a production-ready web application"),
    (r"\bcreate\s+a\s+web\s+app\b", "Build a production-ready web application"),
    (r"\bbuild\s+a\s+web\s+app\b", "Build a production-ready web application"),
    (r"\bmake\s+a\s+dashboard\b", "Build a responsive dashboard"),
    (r"\bcreate\s+a\s+dashboard\b", "Build a responsive dashboard"),
    (r"\bbuild\s+a\s+dashboard\b", "Build a responsive dashboard"),
    (r"\bmake\s+an?\s+API\b", "Build a RESTful API"),
    (r"\bcreate\s+an?\s+API\b", "Build a RESTful API"),
    (r"\bbuild\s+an?\s+API\b", "Build a RESTful API"),
    (r"\bmake\s+a\s+(?:mobile\s+)?app\b", "Build a cross-platform mobile app"),
    (r"\bcreate\s+a\s+(?:mobile\s+)?app\b", "Build a cross-platform mobile app"),
    (r"\bmake\s+a\s+chatbot\b", "Build a conversational AI chatbot"),
    (r"\bcreate\s+a\s+chatbot\b", "Build a conversational AI chatbot"),
    (r"\bmake\s+a\s+CLI\b", "Build a command-line interface tool"),
    (r"\bcreate\s+a\s+CLI\b", "Build a command-line interface tool"),
    (r"\bwrite\s+(?:some\s+)?tests?\b", "Write comprehensive automated tests"),
    (r"\badd\s+(?:some\s+)?tests?\b", "Add comprehensive automated tests"),
    (r"\bwrite\s+(?:some\s+)?documentation\b", "Write clear API documentation"),
    (r"\badd\s+(?:some\s+)?documentation\b", "Add comprehensive documentation"),
    (r"\bsend\s+(?:an?\s+)?email\b", "Send transactional emails"),
    (r"\bhandle\s+(?:file\s+)?upload\b", "Handle file uploads with validation"),
]

# Redundancy groups
REDUNDANCY_GROUPS: List[List[str]] = [
    ["responsive design", "mobile friendly", "mobile-friendly", "mobile responsive",
     "works on mobile", "works on phones", "supports small screens", "mobile support",
     "optimized for mobile", "mobile-first"],
    ["production ready", "production-ready", "production grade", "production-grade",
     "ready for production"],
    ["user friendly", "user-friendly", "easy to use", "intuitive interface",
     "simple to use", "easy-to-use"],
    ["secure", "security", "secure coding", "follow security best practices",
     "implement security", "security best practices"],
    ["performance", "fast", "performant", "high performance", "optimized performance",
     "fast loading", "quick", "efficient"],
    ["scalable", "scalability", "scales well", "horizontally scalable", "designed to scale"],
    ["clean code", "readable code", "well-written code", "maintainable code",
     "good code quality", "code quality"],
]

# Quality adjective → structured requirement label
QUALITY_TO_REQUIREMENT: List[Tuple[str, str]] = [
    (r"\b(?:secure|security|safe|protected)\b", "Security best practices"),
    (r"\b(?:scalable|scalability|scale)\b", "Horizontal scalability"),
    (r"\b(?:fast|performant|performance|high.?performance|optimized|efficient)\b", "High performance"),
    (r"\b(?:documented|documentation|docs)\b", "API documentation"),
    (r"\berror\s+handling\b", "Robust error handling"),
    (r"\b(?:test|tests|tested|testing|coverage)\b", "Test coverage"),
    (r"\b(?:authenticated|authentication|auth)\b", "Authentication"),
    (r"\b(?:authorized|authorization|permissions?|rbac)\b", "Role-based authorization"),
    (r"\b(?:validated|validation|sanitized|sanitization)\b", "Input validation & sanitization"),
    (r"\b(?:logged|logging|logs)\b", "Request logging"),
    (r"\b(?:cached|caching|cache)\b", "Response caching"),
    (r"\b(?:rate.?limit|throttl)\b", "Rate limiting"),
    (r"\b(?:paginated|pagination|paging)\b", "Pagination"),
    (r"\b(?:search|searchable|full.?text)\b", "Search functionality"),
    (r"\b(?:upload|file.?upload)\b", "File upload handling"),
    (r"\b(?:responsive|mobile.?friendly|mobile.?first)\b", "Responsive design"),
    (r"\b(?:accessible|accessibility|a11y)\b", "Accessibility (WCAG)"),
    (r"\b(?:deployed|deployment|ci.?cd|pipeline)\b", "CI/CD deployment pipeline"),
    (r"\b(?:typed|typescript|type.?safe)\b", "TypeScript / strict types"),
    (r"\b(?:realtime|real.?time|websocket|live)\b", "Real-time updates"),
    (r"\b(?:internationali[sz]|i18n|locali[sz])\b", "Internationalization (i18n)"),
    (r"\b(?:dark.?mode|theme|theming)\b", "Dark/light theme support"),
]

# Role prose patterns
ROLE_PROSE_PATTERNS: List[str] = [
    r"I\s+want\s+you\s+to\s+act\s+as\s+[^\n.]+[.\n]?",
    r"You\s+are\s+(?:a\s+|an\s+)?[^\n.]+(?:engineer|developer|expert|specialist)[^\n.]*[.\n]?",
    r"Act\s+as\s+(?:a\s+|an\s+)?[^\n.]+[.\n]?",
    r"Your\s+role\s+is\s+[^\n.]+[.\n]?",
    r"As\s+(?:a\s+|an\s+)?(?:experienced|senior|expert|skilled)\s+[^\n.]+,\s*",
]

# Tech terms that aren't real stack choices
GENERIC_TECH = {"REST", "CSS", "HTML", "HTTP", "HTTPS", "AJAX", "JSON", "XML", "API"}


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
        intent = self.analyzer.analyze(text)

        # Step 1: aggressive cleanup
        cleaned = self._cleanup(text)

        # Step 2: protect constraints before any removal
        protected = intent["constraints"]

        # Step 3: redundancy removal
        deduped = self._remove_redundancy(cleaned)

        # Step 4: structured rewrite based on size
        size = self._effective_size(intent, text)
        if size == "large":
            optimized = self._generate_spec(deduped, intent)
        elif size == "medium":
            optimized = self._medium_optimize(deduped, intent)
        else:
            optimized = self._light_optimize(deduped, intent)

        # Step 5: guarantee constraints survived
        optimized = self._ensure_constraints(optimized, protected)

        return {"optimized": optimized, "intent": intent, "mode": size}

    def _effective_size(self, intent: Dict, text: str) -> str:
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
    # Step 1: Cleanup (filler removal + whitespace)
    # ------------------------------------------------------------------

    def _cleanup(self, text: str) -> str:
        # Strip HTML
        text = re.sub(r"<[^>]+>", " ", text)
        text = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        text = text.replace("&nbsp;", " ").replace("&#x27;", "'")

        # Remove decorative markdown
        text = re.sub(r"^[-*_]{3,}\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\*{3,}", "", text)
        text = re.sub(r"_{3,}", "", text)
        text = re.sub(r"^#{4,}\s*", "### ", text, flags=re.MULTILINE)

        # Compress verbose phrases first (before filler, order matters)
        text = self._compress_verbose(text)

        # Strip filler words and phrases
        text = self._strip_fillers(text)

        # Strip trailing question marks (prompts written as questions)
        text = re.sub(r"\?\s*$", ".", text, flags=re.MULTILINE)
        text = re.sub(r"\?(\s)", r".\1", text)

        # Normalize whitespace
        text = clean_whitespace(text)

        # Remove exact-duplicate lines
        text = self._dedup_lines(text)

        return text

    def _strip_fillers(self, text: str) -> str:
        for pattern, replacement in FILLER_PHRASES:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        # Clean up double spaces and sentence-start artifacts
        text = re.sub(r"[ \t]{2,}", " ", text)
        text = re.sub(r"(?<=[.!?])\s{2,}", " ", text)
        # Fix sentences that now start with lowercase after filler removal
        text = re.sub(
            r"(?<=[.!?]\s)([a-z])",
            lambda m: m.group(1).upper(),
            text
        )
        # Fix line-starts that now begin with lowercase
        text = re.sub(
            r"^([a-z])",
            lambda m: m.group(1).upper(),
            text,
            flags=re.MULTILINE,
        )
        return text

    def _compress_verbose(self, text: str) -> str:
        for pattern, replacement in VERBOSE_MAP:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
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
        paragraphs = split_paragraphs(text)
        if len(paragraphs) > 1:
            encoder = self._get_encoder()
            if encoder and len(paragraphs) > 3:
                paragraphs = self._semantic_dedup(paragraphs, encoder)
            else:
                paragraphs = self._phrase_dedup_paragraphs(paragraphs)
        paragraphs = [self._dedup_bullets_in_block(p) for p in paragraphs]
        return "\n\n".join(p for p in paragraphs if p.strip())

    def _semantic_dedup(self, paragraphs: List[str], encoder) -> List[str]:
        try:
            import numpy as np
            indexed = [(i, p) for i, p in enumerate(paragraphs) if len(p) > 40]
            if len(indexed) < 2:
                return paragraphs
            idxs, texts = zip(*indexed)
            embeddings = encoder.encode(list(texts), show_progress_bar=False)
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
                        keep, drop = (i, j) if len(texts[i]) >= len(texts[j]) else (j, i)
                        to_remove.add(drop)
            kept_positions = {idxs[i] for i in range(len(idxs)) if i not in to_remove}
            return [p for pos, p in enumerate(paragraphs) if len(p) <= 40 or pos in kept_positions]
        except Exception:
            return self._phrase_dedup_paragraphs(paragraphs)

    def _phrase_dedup_paragraphs(self, paragraphs: List[str]) -> List[str]:
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
        lines = text.split("\n")
        used_groups: set[int] = set()
        to_remove: set[int] = set()
        for line_idx, line in enumerate(lines):
            stripped = line.strip()
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

    def _light_optimize(self, text: str, intent: Dict) -> str:
        text = self._apply_enhancements(text)

        # Add role block if present and not already structured
        role = intent.get("role")
        if role and not intent.get("already_structured"):
            text = self._strip_role_prose(text)
            text = f"**Role:** {role.strip().rstrip('.,:')}\n\n{text.strip()}"

        return text.strip()

    # ------------------------------------------------------------------
    # Step 3b: Medium optimization → always produce structured output
    # ------------------------------------------------------------------

    def _medium_optimize(self, text: str, intent: Dict) -> str:
        parts: list[str] = []

        # Role
        role = intent.get("role")
        if role and not intent.get("already_structured"):
            text = self._strip_role_prose(text)
            parts.append(f"**Role:** {role.strip().rstrip('.,:')}")

        # Task — derive a clean imperative sentence
        task = self._build_task_line(text, intent)
        if task:
            parts.append(f"**Task:** {task}")

        # Stack (filter out generic terms)
        tech = [t for t in intent.get("tech_stack", []) if t not in GENERIC_TECH]
        if tech:
            parts.append("**Stack:**\n" + "\n".join(f"- {t}" for t in tech))

        # Requirements — extract from prose
        reqs = self._extract_requirements(text, intent, exclude_tech=tech)
        if reqs:
            parts.append("**Requirements:**\n" + "\n".join(f"- {r}" for r in reqs))

        # Constraints
        constraints = self._dedup_constraints(intent.get("constraints", []))
        if constraints:
            parts.append("**Constraints:**\n" + "\n".join(f"- {c}" for c in constraints[:8]))

        # Output format / deliverables
        deliverables = intent.get("deliverables", [])
        if deliverables:
            parts.append("**Deliverables:**\n" + "\n".join(f"- {d}" for d in deliverables[:4]))

        if len(parts) >= 2:
            return "\n\n".join(parts)

        # Fallback: enhanced + restructured prose
        text = self._apply_enhancements(text.strip())
        text = self._prose_to_bullets(text)
        return text

    def _build_task_line(self, text: str, intent: Dict) -> Optional[str]:
        """Derive a clean, imperative task sentence from the already-cleaned text."""
        TASK_VERBS = re.compile(
            r"^(?:Build|Create|Develop|Write|Design|Implement|Make|Generate|"
            r"Produce|Set\s+up|Refactor|Fix|Migrate|Deploy|Add|Convert|Integrate)",
            re.IGNORECASE,
        )

        # 1. Prefer an imperative line from the already-cleaned text
        for line in text.split("\n")[:10]:
            line = re.sub(r"^#+\s*", "", line.strip())
            if 10 < len(line) < 200 and TASK_VERBS.match(line):
                return self._apply_enhancements(line.rstrip(".?!"))

        # 2. Fall back to intent fields — apply filler/verbose removal here too
        raw = intent.get("task") or intent.get("objective")
        if raw:
            raw = self._compress_verbose(raw)
            raw = self._strip_fillers(raw)
            raw = self._apply_enhancements(raw.strip().rstrip(".?!"))
            raw = re.split(r"(?<=[.!?])\s+", raw)[0]
            if raw:
                return raw[0].upper() + raw[1:]

        # 3. First meaningful line of cleaned text
        for line in text.split("\n")[:8]:
            line = re.sub(r"^#+\s*", "", line.strip())
            if len(line) > 15:
                return self._apply_enhancements(line.rstrip(".?!"))

        return None

    def _extract_requirements(
        self, text: str, intent: Dict, exclude_tech: List[str] = None
    ) -> List[str]:
        """
        Pull requirements from:
        1. Existing bullet points (cleaned)
        2. Modal sentences (should/must/needs to)
        3. Quality adjective → canonical requirement label
        """
        exclude_tech = exclude_tech or []
        reqs: list[str] = []
        seen_keys: set[str] = set()

        def add(r: str) -> None:
            r = r.strip().rstrip(".,;:")
            r = r[0].upper() + r[1:] if r else r
            key = r.lower()[:50]
            if key and key not in seen_keys and len(r) > 4:
                seen_keys.add(key)
                reqs.append(r)

        CONSTRAINT_RE = re.compile(
            r"^(?:do not|don't|must not|never|avoid|preserve|maintain|keep)",
            re.IGNORECASE,
        )
        DELIVERABLE_RE = re.compile(
            r"^(?:complete source|source code|deployment guide|api doc|"
            r"database schema|test suite|user doc|admin guide|unit test)",
            re.IGNORECASE,
        )

        # 1. Existing bullets
        for bullet in re.findall(r"^[-*•]\s+(.+)$", text, re.MULTILINE):
            bullet = bullet.strip()
            if (5 < len(bullet) < 120
                    and not CONSTRAINT_RE.match(bullet)
                    and not DELIVERABLE_RE.match(bullet)):
                # Skip if it's just a tech name we already captured
                if bullet not in exclude_tech:
                    add(bullet)

        # 2. Modal sentences → short requirement phrases
        VAGUE_REQ = re.compile(
            r"^(?:follow best practices?|be good|look good|work well|"
            r"handle (?:many|large number|a lot)|be (?:well[\s-]written|nice|great|amazing)|"
            r"have (?:good|great|nice)|make (?:it|sure)|ensure (?:it|that)$)",
            re.IGNORECASE,
        )
        modal_re = re.compile(
            r"(?:The\s+(?:app|system|API|service|platform|backend|frontend)|It|Users?|Admins?)"
            r"[^\n.]{0,30}(?:should|must|needs?\s+to|has?\s+to|will)\s+"
            r"([^\n.]{10,100})",
            re.IGNORECASE,
        )
        for m in modal_re.finditer(text):
            phrase = m.group(1).strip().rstrip(".,;")
            phrase = re.sub(r"^(?:be\s+able\s+to|support|include|have|provide|allow)\s+", "", phrase, flags=re.IGNORECASE)
            if len(phrase) > 5 and not VAGUE_REQ.match(phrase):
                add(phrase)

        # 3. Quality adjective → canonical label
        text_lower = text.lower()
        for pattern, label in QUALITY_TO_REQUIREMENT:
            if re.search(pattern, text_lower):
                add(label)

        # Deduplicate near-duplicates (shared prefix)
        final: list[str] = []
        final_lower: list[str] = []
        for r in reqs:
            rl = r.lower()
            if not any(rl[:40] in fl or fl[:40] in rl for fl in final_lower):
                final.append(r)
                final_lower.append(rl)

        return final[:14]

    def _apply_enhancements(self, text: str) -> str:
        for pattern, replacement in ENHANCEMENT_MAP:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        return text

    def _prose_to_bullets(self, text: str) -> str:
        def convert_list_sentence(m: re.Match) -> str:
            intro = m.group(1)
            items_raw = m.group(2)
            items = [i.strip() for i in re.split(r",\s*(?:and\s+|or\s+)?", items_raw) if i.strip()]
            if len(items) < 2:
                return m.group(0)
            bullets = "\n".join(f"- {item}" for item in items)
            return f"{intro}:\n{bullets}"

        text = re.sub(
            r"((?:include|support|using|use|require|need|implement)[s]?)\s+"
            r"([a-zA-Z][^.:\n]{15,120}(?:,\s*(?:and\s+|or\s+)?[a-zA-Z][^,.\n]+){1,})",
            convert_list_sentence,
            text,
            flags=re.IGNORECASE,
        )
        return text

    def _strip_role_prose(self, text: str) -> str:
        for pattern in ROLE_PROSE_PATTERNS:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
        return clean_whitespace(text)

    # ------------------------------------------------------------------
    # Step 3c: Spec generation (large prompts)
    # ------------------------------------------------------------------

    def _generate_spec(self, text: str, intent: Dict) -> str:
        sections: Dict[str, str] = {}

        obj = intent.get("objective") or self._first_meaningful_sentence(text)
        if obj:
            first_sentence = re.split(r"(?<=[.!?])\s+", obj)[0]
            first_sentence = self._apply_enhancements(first_sentence.strip().rstrip("."))
            sections["# Objective"] = first_sentence

        users = intent.get("users", [])
        if users:
            sections["# Users"] = "\n".join(f"- {u}" for u in users)

        features = self._extract_features_scoped(text, intent)
        if features:
            sections["# Features"] = "\n".join(f"- {f}" for f in features[:20])

        tech = [t for t in intent.get("tech_stack", []) if t not in GENERIC_TECH]
        if tech:
            sections["# Tech Stack"] = "\n".join(f"- {t}" for t in tech)

        constraints = self._dedup_constraints(intent.get("constraints", []))
        if constraints:
            sections["# Constraints"] = "\n".join(f"- {c}" for c in constraints[:10])

        deliverables = intent.get("deliverables", [])
        if deliverables:
            sections["# Deliverables"] = "\n".join(f"- {d}" for d in deliverables[:6])

        if len(sections) < 2:
            return self._medium_optimize(text, intent)

        return "\n\n".join(f"{header}\n\n{body}" for header, body in sections.items())

    def _first_meaningful_sentence(self, text: str) -> Optional[str]:
        clean = re.sub(r"^#+\s*", "", text, flags=re.MULTILINE)
        sentences = re.split(r"(?<=[.!?])\s+", clean)
        for s in sentences[:6]:
            s = s.strip()
            if len(s) > 20 and re.search(
                r"\b(?:build|create|develop|design|implement|manage|track|provide)\b",
                s, re.IGNORECASE
            ):
                return s
        for line in text.split("\n"):
            line = re.sub(r"^#+\s*", "", line).strip()
            if len(line) > 25:
                return line
        return None

    def _extract_features_scoped(self, text: str, intent: Dict) -> List[str]:
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
        section_re = re.compile(
            r"^(?:#{1,3}\s*)?(?:core\s+)?(?:features?|requirements?|functionality|capabilities)[^\n]*$",
            re.IGNORECASE | re.MULTILINE,
        )
        m = section_re.search(text)
        if m:
            section_text = text[m.end(): m.end() + 800]
            next_header = re.search(r"^#{1,3}\s+\w", section_text, re.MULTILINE)
            if next_header:
                section_text = section_text[: next_header.start()]
            bullets = re.findall(r"^[-*•]\s+(.+)$", section_text, re.MULTILINE)
            for b in bullets:
                b = b.strip()
                if 5 < len(b) < 120 and not CONSTRAINT_RE.match(b) and not DELIVERABLE_RE.match(b):
                    features.append(b)
        if not features:
            all_bullets = re.findall(r"^[-*•]\s+(.+)$", text, re.MULTILINE)
            for b in all_bullets:
                b = b.strip()
                if 5 < len(b) < 120 and not CONSTRAINT_RE.match(b) and not DELIVERABLE_RE.match(b):
                    features.append(b)
        for f in intent.get("features", []):
            if not CONSTRAINT_RE.match(f) and not DELIVERABLE_RE.match(f):
                features.append(f)
        seen: set[str] = set()
        unique: list[str] = []
        for f in features:
            key = f.lower()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _dedup_constraints(self, constraints: List[str]) -> List[str]:
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
        if not constraints:
            return optimized
        missing: list[str] = []
        for c in constraints:
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
