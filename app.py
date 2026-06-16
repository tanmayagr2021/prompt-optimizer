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
)
from utils import calculate_stats

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

def render_sidebar() -> tuple[bool, str | None]:
    """Returns (use_llm, model_name_or_None)."""
    with st.sidebar:
        st.markdown("### ⚙️ Optimization Engine")

        models = _cached_models()
        has_ollama = bool(models)

        if has_ollama:
            default_model = _pick_default_model(models)
            default_idx = models.index(default_model) if default_model in models else 0

            st.markdown(
                '<div class="status-pill status-ai">🟢 Ollama connected</div>',
                unsafe_allow_html=True,
            )

            use_llm = st.toggle("Use AI (Ollama)", value=True)
            model = st.selectbox("Model", models, index=default_idx)

            if use_llm:
                st.caption(f"Using **{model}** for AI-powered optimization.")
            else:
                st.caption("Using fast rule-based optimizer (no AI).")

            return use_llm, model

        else:
            st.markdown(
                '<div class="status-pill status-off">⚪ Ollama not found</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                "**Get AI-quality optimization for free:**\n\n"
                "1. [Download Ollama](https://ollama.com/download) and install it\n"
                "2. Open Terminal and run:\n"
                "```\nollama pull llama3.2\n```\n"
                "3. Refresh this page\n\n"
                "Ollama runs locally — no API key, no cost, fully private."
            )

            st.divider()
            st.caption("Currently using rule-based optimizer.")
            return False, None


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

def main() -> None:
    st.markdown('<p class="app-title">⚡ Prompt Optimizer</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">Reduce AI token usage while preserving intent and quality.</p>',
        unsafe_allow_html=True,
    )

    use_llm, model = render_sidebar()
    optimizer = get_optimizer()
    extractor = get_extractor()

    left, right = st.columns([1, 1], gap="large")

    # ------------------------------------------------------------------ #
    # LEFT — Input
    # ------------------------------------------------------------------ #
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

    # ------------------------------------------------------------------ #
    # RIGHT — Output
    # ------------------------------------------------------------------ #
    with right:
        st.markdown('<p class="section-label">Optimized Prompt</p>', unsafe_allow_html=True)

        if optimize_clicked and user_input.strip():
            t0 = time.perf_counter()
            optimized_text: str | None = None
            used_llm = False

            if use_llm and model:
                with st.spinner(f"Optimizing with {model}…"):
                    optimized_text = optimize_with_llm(user_input, model)
                    if optimized_text:
                        used_llm = True

            if not optimized_text:
                with st.spinner("Optimizing…"):
                    result = optimizer.optimize(user_input)
                    optimized_text = result["optimized"]

            elapsed = time.perf_counter() - t0

            st.session_state["result_text"] = optimized_text
            st.session_state["original"]    = user_input
            st.session_state["elapsed"]     = elapsed
            st.session_state["used_llm"]    = used_llm
            st.session_state["llm_model"]   = model if used_llm else None
            st.session_state["rule_mode"]   = result["mode"] if not used_llm else None

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

        else:
            st.markdown(
                '<div style="color:#9ca3af;font-size:0.95rem;padding-top:2rem;">'
                "Optimized prompt will appear here."
                "</div>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
