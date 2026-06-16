"""
Prompt Optimizer — Streamlit application entry point.
Run with: streamlit run app.py
"""

import time
import streamlit as st

from extractor import FileExtractor
from optimizer import PromptOptimizer
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
# Custom CSS — clean, minimal, single-page feel
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
/* Global */
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }

/* Hide Streamlit branding */
#MainMenu { visibility: hidden; }
footer   { visibility: hidden; }
header   { visibility: hidden; }

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

/* Title area */
.app-title {
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.app-subtitle {
    color: #6b7280;
    font-size: 0.95rem;
    margin-top: 0.25rem;
    margin-bottom: 1.5rem;
}

/* Section labels */
.section-label {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #6b7280;
    margin-bottom: 0.4rem;
}

/* Stat card */
.stat-card {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    text-align: center;
}
.stat-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}
.stat-delta-good  { color: #059669; font-size: 0.8rem; font-weight: 600; }
.stat-delta-none  { color: #6b7280; font-size: 0.8rem; }
.stat-label { font-size: 0.75rem; color: #6b7280; margin-top: 0.2rem; }

/* Mode badge */
.mode-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.mode-small  { background: #dbeafe; color: #1d4ed8; }
.mode-medium { background: #fef3c7; color: #b45309; }
.mode-large  { background: #dcfce7; color: #15803d; }

/* Divider */
.divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 1.5rem 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Cached resource initialisation
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner="Loading optimizer…")
def get_optimizer() -> PromptOptimizer:
    return PromptOptimizer()


@st.cache_resource(show_spinner=False)
def get_extractor() -> FileExtractor:
    return FileExtractor()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mode_badge(mode: str) -> str:
    return f'<span class="mode-badge mode-{mode}">{mode}</span>'


def _format_number(n: int) -> str:
    return f"{n:,}"


# ---------------------------------------------------------------------------
# Main layout
# ---------------------------------------------------------------------------

def main() -> None:
    # Header
    st.markdown('<p class="app-title">⚡ Prompt Optimizer</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="app-subtitle">Reduce AI token usage while preserving intent and quality. '
        "Works with Claude Code, ChatGPT, Gemini, Cursor, Windsurf, and more.</p>",
        unsafe_allow_html=True,
    )

    optimizer = get_optimizer()
    extractor = get_extractor()

    left, right = st.columns([1, 1], gap="large")

    # ------------------------------------------------------------------ #
    # LEFT COLUMN — Input
    # ------------------------------------------------------------------ #
    with left:
        st.markdown('<p class="section-label">Input</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload file",
            type=["pdf", "docx", "txt", "md"],
            label_visibility="collapsed",
            help="Upload a PDF, Word document, or text file to extract its content.",
        )

        # Pre-fill textarea if file was uploaded
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

        optimize_clicked = st.button(
            "⚡ Optimize Prompt",
            type="primary",
            use_container_width=True,
            disabled=not user_input.strip(),
        )

    # ------------------------------------------------------------------ #
    # RIGHT COLUMN — Output
    # ------------------------------------------------------------------ #
    with right:
        st.markdown('<p class="section-label">Optimized Prompt</p>', unsafe_allow_html=True)

        # Run optimization
        if optimize_clicked and user_input.strip():
            with st.spinner("Optimizing…"):
                t0 = time.perf_counter()
                result = optimizer.optimize(user_input)
                elapsed = time.perf_counter() - t0

            st.session_state["result"] = result
            st.session_state["original"] = user_input
            st.session_state["elapsed"] = elapsed

        # Display output
        if "result" in st.session_state:
            result: dict = st.session_state["result"]
            original: str = st.session_state["original"]
            elapsed: float = st.session_state.get("elapsed", 0)
            optimized_text: str = result["optimized"]
            mode: str = result["mode"]

            # Mode indicator
            st.markdown(
                f"Mode: {_mode_badge(mode)} &nbsp; "
                f'<span style="color:#6b7280;font-size:0.8rem;">{elapsed:.2f}s</span>',
                unsafe_allow_html=True,
            )

            # Output box — st.code gives built-in copy button
            st.code(optimized_text, language="markdown")

            # Download buttons
            dl_col1, dl_col2 = st.columns(2)
            with dl_col1:
                st.download_button(
                    "⬇ Download TXT",
                    data=optimized_text,
                    file_name="optimized_prompt.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
            with dl_col2:
                st.download_button(
                    "⬇ Download Markdown",
                    data=optimized_text,
                    file_name="optimized_prompt.md",
                    mime="text/markdown",
                    use_container_width=True,
                )

            # ---------------------------------------------------------- #
            # Statistics
            # ---------------------------------------------------------- #
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<p class="section-label">Statistics</p>', unsafe_allow_html=True)

            stats = calculate_stats(original, optimized_text)
            c1, c2, c3, c4, c5 = st.columns(5)

            with c1:
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-value">{_format_number(stats["original_chars"])}</div>'
                    f'<div class="stat-label">Original chars</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-value">{_format_number(stats["optimized_chars"])}</div>'
                    f'<div class="stat-label">Optimized chars</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with c3:
                removed = stats["chars_removed"]
                sign = "-" if removed >= 0 else "+"
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-value">{sign}{_format_number(abs(removed))}</div>'
                    f'<div class="stat-label">Chars removed</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
            with c4:
                pct = stats["reduction_pct"]
                delta_cls = "stat-delta-good" if pct > 0 else "stat-delta-none"
                st.markdown(
                    f'<div class="stat-card">'
                    f'<div class="stat-value">{pct:.1f}%</div>'
                    f'<div class="{delta_cls}">reduction</div>'
                    f'<div class="stat-label">Char reduction</div>'
                    f"</div>",
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
                    f'<div class="stat-label">Token reduction</div>'
                    f"</div>",
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
