"""Intent analyzer — extracts role, task, tech stack, constraints, and doc type."""

import re
from typing import Dict, List, Optional

# ---------------------------------------------------------------------------
# Technology keyword registry (canonical casing for display)
# ---------------------------------------------------------------------------
TECH_KEYWORDS: list[str] = [
    # Frontend
    "React", "Vue", "Angular", "Next.js", "Nuxt", "Svelte", "Astro", "SvelteKit",
    "Redux", "Zustand", "Tailwind", "Bootstrap", "Material UI", "shadcn",
    # Backend
    "Node.js", "Express", "Fastify", "Hono", "NestJS", "Django", "Flask",
    "FastAPI", "Spring", "Laravel", "Rails", "Phoenix", "Fiber",
    # Languages
    "Python", "JavaScript", "TypeScript", "Go", "Rust", "Java", "C#", "PHP",
    "Ruby", "Elixir", "Kotlin", "Swift",
    # Databases
    "PostgreSQL", "MySQL", "SQLite", "MongoDB", "Redis", "Supabase",
    "PlanetScale", "CockroachDB", "DynamoDB", "Firestore", "Cassandra",
    # Infra / Cloud
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Vercel", "Netlify",
    "Heroku", "Railway", "Fly.io", "Terraform", "Ansible",
    # APIs / protocols
    "GraphQL", "REST", "gRPC", "WebSocket", "tRPC", "OpenAPI",
    # Testing
    "Jest", "Vitest", "Pytest", "Playwright", "Cypress",
    # Other
    "Stripe", "Twilio", "SendGrid", "Cloudflare", "Nginx",
    "Elasticsearch", "RabbitMQ", "Kafka", "Celery", "Prisma", "Drizzle",
]

# Phrases that indicate a constraint
CONSTRAINT_PATTERNS: list[str] = [
    r"(?:do not|don't|must not|cannot|can't|never)\s+[^\n.]{5,120}",
    r"(?:preserve|maintain|keep|protect|retain)\s+[^\n.]{5,120}",
    r"(?:must|should)\s+(?:only|always)\s+[^\n.]{5,120}",
    r"(?:do not modify|do not change|do not remove|do not break)\s+[^\n.]{5,120}",
    r"(?:use only|only use)\s+[^\n.]{5,120}",
    r"backward[- ]?compat(?:ible|ibility)[^\n.]{0,100}",
    r"no breaking changes[^\n.]{0,80}",
    r"API compat(?:ible|ibility)[^\n.]{0,80}",
]

# Role extraction patterns
ROLE_PATTERNS: list[str] = [
    r"(?:act as|you are|acting as|your role is?)\s+(?:a\s+|an\s+)?([^\n.,]{5,80})",
    r"^role:\s*(.+)$",
    r"(?:as\s+a\s+|as\s+an\s+)([^\n,]{5,60}(?:engineer|developer|designer|analyst|architect|expert|specialist|lead|manager|consultant|scientist))",
]

# Task extraction: starts with an imperative verb
TASK_VERBS = r"^(?:Build|Create|Develop|Write|Design|Implement|Make|Generate|Produce|Set up|Setup|Refactor|Fix|Migrate|Deploy)"

# Document classification indicators
DOC_SIGNALS: dict[str, list[str]] = {
    "prd": [
        "user story", "acceptance criteria", "product requirement", "prd",
        "roadmap", "milestone", "sprint", "backlog", "epic",
    ],
    "spec": [
        "technical specification", "system design", "architecture diagram",
        "api design", "data model", "entity relationship",
    ],
    "meeting": [
        "meeting notes", "agenda", "action items", "attendees", "minutes",
        "follow-up", "next steps",
    ],
    "business": [
        "business plan", "executive summary", "market analysis",
        "revenue model", "go-to-market",
    ],
}


class IntentAnalyzer:
    """Analyzes a prompt and extracts structured intent information."""

    def __init__(self) -> None:
        self._nlp = None
        self._nlp_loaded = False

    def _get_nlp(self):
        """Lazy-load spaCy model; silently skip if unavailable."""
        if self._nlp_loaded:
            return self._nlp
        self._nlp_loaded = True
        try:
            import spacy  # noqa: F401
            self._nlp = spacy.load("en_core_web_sm")
        except Exception:
            self._nlp = None
        return self._nlp

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self, text: str) -> Dict:
        """Return a dict with all extracted intent components."""
        return {
            "role": self._extract_role(text),
            "task": self._extract_task(text),
            "tech_stack": self._extract_tech_stack(text),
            "constraints": self._extract_constraints(text),
            "deliverables": self._extract_deliverables(text),
            "users": self._extract_users(text),
            "features": self._extract_features(text),
            "objective": self._extract_objective(text),
            "doc_type": self._classify_document(text),
            "prompt_size": self._classify_size(text),
            "already_structured": self._is_well_structured(text),
        }

    # ------------------------------------------------------------------
    # Extraction helpers
    # ------------------------------------------------------------------

    def _extract_role(self, text: str) -> Optional[str]:
        for pattern in ROLE_PATTERNS:
            m = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if m:
                role = m.group(1).strip().rstrip(".,:")
                if len(role) > 3:
                    return role
        return None

    def _extract_task(self, text: str) -> Optional[str]:
        for line in text.split("\n")[:10]:
            line = line.strip()
            if 10 < len(line) < 200 and re.match(TASK_VERBS, line, re.IGNORECASE):
                return line.rstrip(".")
        return None

    def _extract_tech_stack(self, text: str) -> List[str]:
        text_lower = text.lower()
        found = []
        for tech in TECH_KEYWORDS:
            # Whole-word match (handles "Vue" vs "Vue.js" etc.)
            pattern = re.escape(tech.lower())
            if re.search(r"\b" + pattern + r"\b", text_lower):
                found.append(tech)
        return found

    def _extract_constraints(self, text: str) -> List[str]:
        constraints: list[str] = []
        for pattern in CONSTRAINT_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            constraints.extend(m.strip().rstrip(".,") for m in matches)
        # Deduplicate while preserving order
        seen: set[str] = set()
        unique: list[str] = []
        for c in constraints:
            key = c.lower()[:60]
            if key not in seen:
                seen.add(key)
                unique.append(c)
        return unique[:12]

    def _extract_deliverables(self, text: str) -> List[str]:
        pattern = r"(?:provide|generate|deliver|produce|output|return)\s+(?:a\s+|an\s+|the\s+)?[^\n.]{10,100}"
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [m.strip().rstrip(".,") for m in matches[:6]]

    def _extract_users(self, text: str) -> List[str]:
        """
        Find user roles by looking for them near role-context phrases, not
        just anywhere in the text (to avoid false positives like 'users can').
        """
        # Each tuple: (search_pattern, display_name)
        role_candidates = [
            (r"\badmins?\b",          "Admin"),
            (r"\badministrators?\b",  "Administrator"),
            (r"\bstaff\b",            "Staff"),
            (r"\bemployees?\b",       "Employee"),
            (r"\bmanagers?\b",        "Manager"),
            (r"\bcustomers?\b",       "Customer"),
            (r"\bguests?\b",          "Guest"),
            (r"\bsubscribers?\b",     "Subscriber"),
            (r"\bclients?\b",         "Client"),
            (r"\beditors?\b",         "Editor"),
            (r"\boperators?\b",       "Operator"),
            (r"\bsuperusers?\b",      "Superuser"),
            (r"\bmoderators?\b",      "Moderator"),
            (r"\bviewers?\b",         "Viewer"),
        ]

        # Context phrases that signal a "users / roles" section
        ROLE_CONTEXT = re.compile(
            r"(?:user[s]?\s+and\s+roles?|roles?\s+and\s+permissions?|"
            r"types?\s+of\s+users?|user\s+types?|accounts?\s+types?|"
            r"there\s+(?:are|will\s+be)\s+(?:\w+\s+)?(?:types?|kinds?)\s+of)",
            re.IGNORECASE,
        )

        # If the doc has a role-context phrase, extract within ±600 chars of it
        m = ROLE_CONTEXT.search(text)
        search_zone = text[max(0, m.start() - 50): m.end() + 600] if m else text
        search_lower = search_zone.lower()

        found = []
        for pattern, display in role_candidates:
            if re.search(pattern, search_lower):
                found.append(display)

        # Always include Admin if text describes admin-level permissions
        if re.search(r"\badmins?\b", text.lower()) and "Admin" not in found:
            found.insert(0, "Admin")

        return list(dict.fromkeys(found))[:6]

    def _extract_features(self, text: str) -> List[str]:
        # Constraint/negative indicators — lines with these are NOT features
        CONSTRAINT_MARKERS = re.compile(
            r"^(?:do not|don't|must not|never|avoid|preserve|maintain|keep|do not modify)",
            re.IGNORECASE,
        )

        features: list[str] = []

        # Existing bullet points are often features (skip constraint bullets)
        bullet_lines = re.findall(r"^[-*•]\s+(.+)$", text, re.MULTILINE)
        for line in bullet_lines:
            line = line.strip()
            if 5 < len(line) < 120 and not CONSTRAINT_MARKERS.match(line):
                features.append(line)

        # Sentences with modal verbs (should, must, will, can)
        modal_sentences = re.findall(
            r"(?:The system|Users?|Admins?|The app)[^\n.]{0,20}(?:should|must|will|can)\s+[^\n.]{10,100}",
            text,
            re.IGNORECASE,
        )
        features.extend(s.strip().rstrip(".,") for s in modal_sentences)

        # Deduplicate
        seen: set[str] = set()
        unique: list[str] = []
        for f in features:
            key = f.lower()[:50]
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique[:20]

    def _extract_objective(self, text: str) -> Optional[str]:
        # Prefer a sentence that contains a build/create verb
        for line in text.split("\n")[:15]:
            line = line.strip()
            if len(line) > 20 and re.search(
                r"\b(?:build|create|develop|design|implement|make)\b", line, re.IGNORECASE
            ):
                return line.rstrip(".")
        # Fallback: first meaningful sentence
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for s in sentences[:3]:
            s = s.strip()
            if len(s) > 20:
                return s.rstrip(".")
        return None

    # ------------------------------------------------------------------
    # Classification helpers
    # ------------------------------------------------------------------

    def _classify_document(self, text: str) -> str:
        text_lower = text.lower()
        best, best_score = "general", 0
        for doc_type, signals in DOC_SIGNALS.items():
            score = sum(1 for kw in signals if kw in text_lower)
            if score > best_score:
                best, best_score = doc_type, score
        return best

    def _classify_size(self, text: str) -> str:
        n = len(text)
        if n < 500:
            return "small"
        if n < 3_000:
            return "medium"
        return "large"

    def _is_well_structured(self, text: str) -> bool:
        has_headers = bool(re.search(r"^#{1,3}\s+\w", text, re.MULTILINE))
        has_bullets = bool(re.search(r"^[-*•]\s+\w", text, re.MULTILINE))
        return has_headers or has_bullets
