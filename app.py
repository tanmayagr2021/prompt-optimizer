"""
Prompt Optimizer — Streamlit application entry point.
Run with: streamlit run app.py
"""

import time
import streamlit as st

from extractor import FileExtractor
from optimizer import PromptOptimizer
from llm_backend import (
    ollama_available,
    get_available_models,
    optimize_with_llm,
    _pick_default_model,
    optimize_with_groq,
    GROQ_MODELS,
)
from architect import (
    PLATFORMS,
    architect_with_groq,
    architect_with_ollama,
    parse_architect_output,
)
from utils import calculate_stats

# ── Resolve API key: Streamlit secrets → env var → None ───────────────────
import os
def _get_groq_key() -> str:
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
#MainMenu { visibility: hidden; }
footer   { visibility: hidden; }
header   { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }

.app-title    { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0; }
.app-subtitle { color: #6b7280; font-size: 0.95rem; margin-top: 0.25rem; margin-bottom: 1.5rem; }

.section-label {
    font-size: 0.8rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.08em; color: #6b7280; margin-bottom: 0.4rem;
}

/* Status pill */
.status-pill {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 999px; font-size: 0.75rem;
    font-weight: 600; margin-bottom: 1rem;
}
.status-ai   { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.status-rule { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.status-off  { background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb; }

/* Mode badge */
.mode-badge {
    display: inline-block; padding: 2px 10px; border-radius: 999px;
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em;
}
.mode-small  { background: #dbeafe; color: #1d4ed8; }
.mode-medium { background: #fef3c7; color: #b45309; }
.mode-large  { background: #dcfce7; color: #15803d; }
.mode-ai     { background: #f3e8ff; color: #7c3aed; }

/* Stat card */
.stat-card  { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 0.75rem 1rem; text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: #111827; line-height: 1.2; }
.stat-delta-good { color: #059669; font-size: 0.8rem; font-weight: 600; }
.stat-delta-none { color: #6b7280; font-size: 0.8rem; }
.stat-label      { font-size: 0.75rem; color: #6b7280; margin-top: 0.2rem; }

.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }

/* Ollama install box */
.install-box {
    background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px;
    padding: 0.75rem 1rem; font-size: 0.85rem; color: #92400e; margin-bottom: 1rem;
}

/* Platform grid */
.platform-grid {
    display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 1rem;
}
.platform-chip {
    padding: 6px 14px; border-radius: 999px; font-size: 0.8rem; font-weight: 600;
    border: 2px solid #e5e7eb; background: #f9fafb; color: #374151;
    cursor: pointer; transition: all 0.15s ease;
}
.platform-chip:hover  { border-color: #6366f1; color: #6366f1; background: #eef2ff; }
.platform-chip.active { border-color: #6366f1; color: #6366f1; background: #eef2ff; }

/* Architect analysis box */
.arch-analysis {
    background: #f8faff; border: 1px solid #c7d2fe; border-radius: 10px;
    padding: 1rem 1.25rem; margin-bottom: 1rem;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cached resource initialisation
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading rule-based optimizer…")
def get_optimizer() -> PromptOptimizer:
    return PromptOptimizer()


@st.cache_resource(show_spinner=False)
def get_extractor() -> FileExtractor:
    return FileExtractor()


@st.cache_data(ttl=10, show_spinner=False)
def _cached_models() -> list[str]:
    return get_available_models()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mode_badge(mode: str, use_llm: bool) -> str:
    if use_llm:
        return '<span class="mode-badge mode-ai">AI</span>'
    return f'<span class="mode-badge mode-{mode}">{mode}</span>'


def _format_number(n: int) -> str:
    return f"{n:,}"


# ---------------------------------------------------------------------------
# Sidebar — Ollama / model settings
# ---------------------------------------------------------------------------

def render_sidebar() -> tuple[bool, str, str]:
    """Returns (use_llm, backend, model_or_key)."""
    with st.sidebar:
        st.markdown("### ⚙️ Optimization Engine")

        groq_key  = _get_groq_key()
        ollama_ok = bool(_cached_models())
        groq_ok   = bool(groq_key)

        # ── Groq (cloud) ──────────────────────────────────────────────────
        if groq_ok:
            st.markdown(
                '<div class="status-pill status-ai">🟢 Groq AI connected</div>',
                unsafe_allow_html=True,
            )
            use_llm = st.toggle("Use AI (Groq)", value=True)
            model   = st.selectbox("Model", GROQ_MODELS)
            if use_llm:
                st.caption(f"Using **{model}** via Groq cloud (free).")
            else:
                st.caption("Using rule-based optimizer.")
            return use_llm, "groq", model

        # ── Ollama (local) ─────────────────────────────────────────────────
        elif ollama_ok:
            models = _cached_models()
            default = _pick_default_model(models)
            idx = models.index(default) if default in models else 0
            st.markdown(
                '<div class="status-pill status-ai">🟢 Ollama connected</div>',
                unsafe_allow_html=True,
            )
            use_llm = st.toggle("Use AI (Ollama)", value=True)
            model   = st.selectbox("Model", models, index=idx)
            if use_llm:
                st.caption(f"Using **{model}** locally via Ollama.")
            else:
                st.caption("Using rule-based optimizer.")
            return use_llm, "ollama", model

        # ── No AI available ────────────────────────────────────────────────
        else:
            st.markdown(
                '<div class="status-pill status-off">⚪ No AI backend</div>',
                unsafe_allow_html=True,
            )
            st.markdown("**Enable AI optimization (free):**")
            with st.expander("☁️ Groq — recommended for hosted app"):
                st.markdown(
                    "1. Get a free key at [console.groq.com](https://console.groq.com)\n"
                    "2. Paste it below:"
                )
                manual_key = st.text_input("Groq API key", type="password", key="groq_manual")
                if manual_key:
                    st.session_state["groq_key_manual"] = manual_key
                    st.rerun()
            with st.expander("🖥️ Ollama — for local / offline use"):
                st.markdown(
                    "1. [Download Ollama](https://ollama.com/download)\n"
                    "2. Run: `ollama pull llama3.2`\n"
                    "3. Refresh this page"
                )
            st.divider()
            st.caption("Currently using rule-based optimizer.")
            return False, "rules", ""


# ---------------------------------------------------------------------------
# PromptArchitect tab
# ---------------------------------------------------------------------------

# Platform category metadata for display
_PLATFORM_META = {
    "Claude":         ("🟣", "Anthropic"),
    "ChatGPT":        ("🟢", "OpenAI"),
    "Gemini":         ("🔵", "Google"),
    "Cursor":         ("⬛", "Code IDE"),
    "Windsurf":       ("🟤", "Code IDE"),
    "Lovable":        ("🩷", "Full-stack"),
    "Bolt":           ("⚡", "Full-stack"),
    "Replit Agent":   ("🟠", "Agent"),
    "Manus":          ("🤖", "Agent"),
    "Perplexity":     ("🔍", "Research"),
    "Midjourney":     ("🎨", "Image"),
    "Flux":           ("🎨", "Image"),
    "Stable Diffusion": ("🎨", "Image"),
}


def render_architect_tab(
    use_llm: bool,
    backend: str,
    model: str,
    groq_key: str,
) -> None:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<p class="section-label">Target Platform</p>', unsafe_allow_html=True)

        # Platform selector
        platform = st.selectbox(
            "Platform",
            PLATFORMS,
            format_func=lambda p: f"{_PLATFORM_META[p][0]}  {p}  ·  {_PLATFORM_META[p][1]}",
            label_visibility="collapsed",
        )

        # Show platform badge
        icon, category = _PLATFORM_META[platform]
        st.markdown(
            f'<div style="margin-bottom:1rem;">'
            f'<span style="background:#eef2ff;color:#4f46e5;border:1px solid #c7d2fe;'
            f'border-radius:999px;padding:4px 14px;font-size:0.8rem;font-weight:600;">'
            f'{icon} {platform} &nbsp;·&nbsp; {category}</span></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<p class="section-label">Your Request</p>', unsafe_allow_html=True)
        user_request: str = st.text_area(
            "Describe what you want",
            height=340,
            placeholder=(
                "Describe your goal in plain language — any length, any detail level.\n\n"
                "Examples:\n"
                "• Build a SaaS landing page with waitlist signup\n"
                "• Write a market research report on AI coding tools\n"
                "• Create a cyberpunk cityscape at dusk, neon-lit rain\n"
                "• Build an e-commerce app with Stripe and auth\n"
                "• Analyze our Q3 churn data and surface root causes"
            ),
            label_visibility="collapsed",
        )

        char_count = len(user_request)
        if char_count:
            st.caption(f"{_format_number(char_count)} characters · ~{_format_number(char_count // 4)} tokens")

        btn_disabled = not user_request.strip() or not use_llm
        generate_clicked = st.button(
            "🏗️ Architect Prompt",
            type="primary",
            use_container_width=True,
            disabled=btn_disabled,
            key="arch_generate",
        )

        if not use_llm:
            st.markdown(
                '<div class="install-box">⚠️ PromptArchitect requires an AI backend. '
                'Connect Groq or Ollama in the sidebar.</div>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<p class="section-label">Generated Prompt</p>', unsafe_allow_html=True)

        if generate_clicked and user_request.strip() and use_llm:
            t0 = time.perf_counter()
            with st.spinner(f"Running 6-phase architecture for {platform}…"):
                if backend == "groq":
                    raw = architect_with_groq(user_request, platform, groq_key, model)
                else:
                    raw = architect_with_ollama(user_request, platform, model)
            elapsed = time.perf_counter() - t0

            if raw:
                parsed = parse_architect_output(raw)
                st.session_state["arch_result"]   = parsed
                st.session_state["arch_platform"] = platform
                st.session_state["arch_model"]    = model
                st.session_state["arch_elapsed"]  = elapsed
            else:
                st.error("Architecture failed — check your backend connection and try again.")

        if "arch_result" in st.session_state:
            parsed   = st.session_state["arch_result"]
            plat     = st.session_state.get("arch_platform", "")
            arch_mdl = st.session_state.get("arch_model", "")
            arch_sec = st.session_state.get("arch_elapsed", 0.0)
            icon_p, _ = _PLATFORM_META.get(plat, ("🤖", ""))

            # Header pill
            st.markdown(
                f'<span class="status-pill status-ai">'
                f'{icon_p} Optimized for {plat}</span>'
                f'&nbsp;<span style="color:#6b7280;font-size:0.8rem;">'
                f'{arch_mdl} · {arch_sec:.1f}s</span>',
                unsafe_allow_html=True,
            )

            # Prompt Analysis
            if parsed["analysis"]:
                with st.expander("📊 Prompt Analysis", expanded=True):
                    st.markdown(parsed["analysis"])

            # The prompt
            st.markdown('<p class="section-label" style="margin-top:0.5rem;">Optimized Prompt</p>', unsafe_allow_html=True)
            st.code(parsed["prompt"], language="markdown")

            dl1, dl2 = st.columns(2)
            safe_name = plat.lower().replace(" ", "_")
            with dl1:
                st.download_button(
                    "⬇ Download TXT",
                    data=parsed["prompt"],
                    file_name=f"prompt_{safe_name}.txt",
                    mime="text/plain",
                    use_container_width=True,
                    key="arch_dl_txt",
                )
            with dl2:
                st.download_button(
                    "⬇ Download Markdown",
                    data=parsed["prompt"],
                    file_name=f"prompt_{safe_name}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="arch_dl_md",
                )

            # Enhancements
            if parsed["enhancements"]:
                with st.expander("✨ Enhancements Added"):
                    st.markdown(parsed["enhancements"])

        else:
            st.markdown(
                '<div style="color:#9ca3af;font-size:0.95rem;padding-top:2rem;">'
                "Your production-grade prompt will appear here."
                "</div>",
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

def main() -> None:
    st.markdown('<p class="app-title">⚡ Prompt Optimizer</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">'
        'Optimize existing prompts — or architect new ones from scratch for any AI platform.'
        '</p>',
        unsafe_allow_html=True,
    )

    use_llm, backend, model = render_sidebar()
    # Allow manually-entered Groq key from sidebar
    if not _get_groq_key() and st.session_state.get("groq_key_manual"):
        groq_key = st.session_state["groq_key_manual"]
        backend  = "groq"
        use_llm  = True
    else:
        groq_key = _get_groq_key()
    optimizer = get_optimizer()
    extractor = get_extractor()

    tab1, tab2 = st.tabs(["⚡ Prompt Optimizer", "🏗️ PromptArchitect"])

    # ------------------------------------------------------------------ #
    # TAB 1 — Prompt Optimizer (existing)
    # ------------------------------------------------------------------ #
    with tab1:
        left, right = st.columns([1, 1], gap="large")

        # LEFT — Input
        with left:
            st.markdown('<p class="section-label">Input</p>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Upload file",
                type=["pdf", "docx", "txt", "md"],
                label_visibility="collapsed",
                help="Upload a PDF, Word document, or text file.",
            )

            prefill = ""
            if uploaded_file is not None:
                file_key = f"file_{uploaded_file.name}_{uploaded_file.size}"
                if st.session_state.get("_last_file") != file_key:
                    with st.spinner(f"Extracting text from {uploaded_file.name}…"):
                        prefill = extractor.extract(uploaded_file)
                    st.session_state["_last_file"] = file_key
                    st.session_state["_prefill"] = prefill
                else:
                    prefill = st.session_state.get("_prefill", "")

            user_input: str = st.text_area(
                "Paste your prompt",
                value=prefill,
                height=420,
                placeholder=(
                    "Paste your prompt here…\n\n"
                    "Examples:\n"
                    "• Claude Code / Cursor / Windsurf instructions\n"
                    "• ChatGPT or Gemini prompts\n"
                    "• PRDs, meeting notes, specs, business plans"
                ),
                label_visibility="collapsed",
            )

            char_count = len(user_input)
            st.caption(f"{_format_number(char_count)} characters · ~{_format_number(char_count // 4)} tokens")

            btn_label = "⚡ Optimize with AI" if use_llm else "⚡ Optimize Prompt"
            optimize_clicked = st.button(
                btn_label,
                type="primary",
                use_container_width=True,
                disabled=not user_input.strip(),
            )

        # RIGHT — Output
        with right:
            st.markdown('<p class="section-label">Optimized Prompt</p>', unsafe_allow_html=True)

            if optimize_clicked and user_input.strip():
                t0 = time.perf_counter()
                optimized_text: str | None = None
                used_llm = False
                result = None

                if use_llm and model:
                    with st.spinner(f"Running 6-pass optimization with {model}…"):
                        if backend == "groq":
                            optimized_text = optimize_with_groq(user_input, groq_key, model)
                        else:
                            optimized_text = optimize_with_llm(user_input, model)
                        if optimized_text:
                            used_llm = True

                if not optimized_text:
                    with st.spinner("Running 6-pass optimization…"):
                        result = optimizer.optimize(user_input)
                        optimized_text = result["optimized"]

                elapsed = time.perf_counter() - t0

                st.session_state["result_text"] = optimized_text
                st.session_state["original"]    = user_input
                st.session_state["elapsed"]     = elapsed
                st.session_state["used_llm"]    = used_llm
                st.session_state["llm_model"]   = model if used_llm else None
                st.session_state["rule_mode"]   = result["mode"] if result else None
                st.session_state["warnings"]    = result["warnings"] if result else []
                st.session_state["score"]       = result["score"] if result else None
                st.session_state["impossible"]  = result.get("impossible_fixes", []) if result else []
                st.session_state["contradictions"] = result.get("contradictions", []) if result else []

            if "result_text" in st.session_state:
                optimized_text: str = st.session_state["result_text"]
                original: str       = st.session_state["original"]
                elapsed: float      = st.session_state.get("elapsed", 0)
                used_llm: bool      = st.session_state.get("used_llm", False)
                llm_model: str      = st.session_state.get("llm_model") or ""
                rule_mode: str      = st.session_state.get("rule_mode") or "medium"

                # Mode indicator
                if used_llm:
                    pill = '<span class="status-pill status-ai">🤖 AI optimized</span>'
                    model_label = f'<span style="color:#6b7280;font-size:0.8rem;">{llm_model} · {elapsed:.1f}s</span>'
                    st.markdown(f"{pill} &nbsp; {model_label}", unsafe_allow_html=True)
                else:
                    badge = _mode_badge(rule_mode, False)
                    st.markdown(
                        f"Mode: {badge} &nbsp; "
                        f'<span style="color:#6b7280;font-size:0.8rem;">{elapsed:.2f}s (rule-based)</span>',
                        unsafe_allow_html=True,
                    )

                # Warnings
                warnings    = st.session_state.get("warnings", [])
                impossible  = st.session_state.get("impossible", [])
                contradicts = st.session_state.get("contradictions", [])

                if impossible:
                    with st.expander(f"⚠️ {len(impossible)} impossible requirement(s) rewritten", expanded=True):
                        for fix in impossible:
                            st.markdown(f"**Original:** `{fix['match']}`  \n**Rewritten to:** {fix['rewrite']}")
                if contradicts:
                    with st.expander(f"🔀 {len(contradicts)} contradiction(s) resolved", expanded=True):
                        for c in contradicts:
                            st.markdown(f"**{c['label'].title()}** — {c['resolution']}")

                st.code(optimized_text, language="markdown")

                dl1, dl2 = st.columns(2)
                with dl1:
                    st.download_button(
                        "⬇ Download TXT",
                        data=optimized_text,
                        file_name="optimized_prompt.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )
                with dl2:
                    st.download_button(
                        "⬇ Download Markdown",
                        data=optimized_text,
                        file_name="optimized_prompt.md",
                        mime="text/markdown",
                        use_container_width=True,
                    )

                # Stats
                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown('<p class="section-label">Statistics</p>', unsafe_allow_html=True)

                stats = calculate_stats(original, optimized_text)
                c1, c2, c3, c4, c5 = st.columns(5)

                with c1:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-value">{_format_number(stats["original_chars"])}</div>'
                        f'<div class="stat-label">Original chars</div></div>',
                        unsafe_allow_html=True,
                    )
                with c2:
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-value">{_format_number(stats["optimized_chars"])}</div>'
                        f'<div class="stat-label">Optimized chars</div></div>',
                        unsafe_allow_html=True,
                    )
                with c3:
                    removed = stats["chars_removed"]
                    sign = "-" if removed >= 0 else "+"
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-value">{sign}{_format_number(abs(removed))}</div>'
                        f'<div class="stat-label">Chars removed</div></div>',
                        unsafe_allow_html=True,
                    )
                with c4:
                    pct = stats["reduction_pct"]
                    delta_cls = "stat-delta-good" if pct > 0 else "stat-delta-none"
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-value">{pct:.1f}%</div>'
                        f'<div class="{delta_cls}">reduction</div>'
                        f'<div class="stat-label">Char reduction</div></div>',
                        unsafe_allow_html=True,
                    )
                with c5:
                    t_pct = stats["token_reduction_pct"]
                    t_removed = stats["token_reduction"]
                    delta_cls = "stat-delta-good" if t_pct > 0 else "stat-delta-none"
                    st.markdown(
                        f'<div class="stat-card">'
                        f'<div class="stat-value">{t_pct:.1f}%</div>'
                        f'<div class="{delta_cls}">~{_format_number(abs(t_removed))} tokens saved</div>'
                        f'<div class="stat-label">Token reduction</div></div>',
                        unsafe_allow_html=True,
                    )

                # Quality score (rule-based only)
                score = st.session_state.get("score")
                if score and not used_llm:
                    st.markdown('<hr class="divider">', unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Quality Score</p>', unsafe_allow_html=True)
                    grade_color = {"A":"#15803d","B":"#1d4ed8","C":"#b45309","D":"#dc2626","F":"#7f1d1d"}.get(score.get("grade","F"),"#6b7280")
                    st.markdown(
                        f'<div style="font-size:2rem;font-weight:700;color:{grade_color};">'
                        f'{score.get("overall",0)}/100 &nbsp; <span style="font-size:1.2rem;">{score.get("grade","?")}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    dims = [
                        ("Clarity",               "clarity"),
                        ("Specificity",           "specificity"),
                        ("Hallucination Resist.", "hallucination_resistance"),
                        ("Research Quality",      "research_quality"),
                        ("Output Structure",      "output_structure"),
                        ("Token Efficiency",      "token_efficiency"),
                        ("Contradiction Score",   "contradiction_score"),
                        ("Impossible Req. Score", "impossible_requirement_score"),
                    ]
                    cols = st.columns(4)
                    for i, (label, key) in enumerate(dims):
                        val = score.get(key, 0)
                        color = "#15803d" if val >= 8 else "#b45309" if val >= 5 else "#dc2626"
                        with cols[i % 4]:
                            st.markdown(
                                f'<div class="stat-card">'
                                f'<div class="stat-value" style="color:{color};font-size:1.2rem;">{val}/10</div>'
                                f'<div class="stat-label">{label}</div></div>',
                                unsafe_allow_html=True,
                            )

            else:
                st.markdown(
                    '<div style="color:#9ca3af;font-size:0.95rem;padding-top:2rem;">'
                    "Optimized prompt will appear here."
                    "</div>",
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------------ #
    # TAB 2 — PromptArchitect
    # ------------------------------------------------------------------ #
    with tab2:
        render_architect_tab(use_llm, backend, model, groq_key)


if __name__ == "__main__":
    main()
