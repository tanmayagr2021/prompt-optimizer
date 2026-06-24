"""
Prompt Optimizer — AI-native redesign.
Run with: streamlit run app.py
"""

import os
import time
import streamlit as st
try:
    from streamlit import iframe as _st_iframe
    _HAS_IFRAME = True
except ImportError:
    import streamlit.components.v1 as _components
    _HAS_IFRAME = False

from extractor import FileExtractor
from optimizer import PromptOptimizer
from llm_backend import (
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
    parse_quality_score,
)
from utils import calculate_stats, analyze_changes
from guidance import (
    LEARNING_CONTENT,
    get_contextual_tip,
    get_rotating_tips,
    get_empty_state_example,
)

st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ── CSS Theme ─────────────────────────────────────────────────────────────────

def _css(dark: bool) -> str:
    if dark:
        bg      = "#0a0a0a"
        bg2     = "#111111"
        bg3     = "#1c1c1c"
        border  = "#2a2a2a"
        border2 = "#3d3d3d"
        text    = "#f0f0f0"
        text2   = "#a0a0a0"
        text3   = "#555555"
        acc     = "#818cf8"
        acc_bg  = "rgba(99,102,241,0.15)"
        acc_txt = "#a5b4fc"
        succ    = "#34d399"
        succ_bg = "rgba(52,211,153,0.12)"
        warn    = "#fcd34d"
        warn_bg = "rgba(252,211,77,0.12)"
        err_bg  = "rgba(248,113,113,0.12)"
        code_bg = "#161616"
        sh      = "0 1px 3px rgba(0,0,0,0.5)"
        sh_md   = "0 4px 16px rgba(0,0,0,0.6)"
        tip_bg  = "linear-gradient(135deg,#1e1b4b 0%,#1a1940 100%)"
        tip_brd = "#3730a3"
        tip_ttl = "#e0e7ff"
        tip_bod = "#a5b4fc"
        tip_tag = "rgba(99,102,241,0.25)"
    else:
        bg      = "#ffffff"
        bg2     = "#f9fafb"
        bg3     = "#f3f4f6"
        border  = "#e5e7eb"
        border2 = "#d1d5db"
        text    = "#111827"
        text2   = "#6b7280"
        text3   = "#9ca3af"
        acc     = "#6366f1"
        acc_bg  = "#eef2ff"
        acc_txt = "#4f46e5"
        succ    = "#059669"
        succ_bg = "#d1fae5"
        warn    = "#d97706"
        warn_bg = "#fef3c7"
        err_bg  = "#fee2e2"
        code_bg = "#f8fafc"
        sh      = "0 1px 3px rgba(0,0,0,0.08)"
        sh_md   = "0 4px 16px rgba(0,0,0,0.1)"
        tip_bg  = "linear-gradient(135deg,#eef2ff 0%,#e0e7ff 100%)"
        tip_brd = "#c7d2fe"
        tip_ttl = "#1e1b4b"
        tip_bod = "#4338ca"
        tip_tag = "rgba(99,102,241,0.1)"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {{
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, system-ui, sans-serif !important;
    -webkit-font-smoothing: antialiased;
    color: {text} !important;
}}

.stApp {{ background: {bg} !important; }}

.main .block-container {{
    padding: 0 2rem 5rem 2rem !important;
    max-width: 1380px !important;
}}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 5px; height: 5px; }}
::-webkit-scrollbar-track {{ background: {bg2}; }}
::-webkit-scrollbar-thumb {{ background: {border2}; border-radius: 3px; }}
::-webkit-scrollbar-thumb:hover {{ background: {text3}; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {bg2} !important;
    border-right: 1px solid {border} !important;
}}
section[data-testid="stSidebar"] * {{ color: {text} !important; }}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] label {{ color: {text} !important; }}

/* ── Text areas ── */
.stTextArea textarea {{
    background: {bg2} !important;
    color: {text} !important;
    border: 1.5px solid {border} !important;
    border-radius: 10px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    line-height: 1.65 !important;
    padding: 0.75rem 1rem !important;
    box-shadow: {sh} !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    resize: vertical !important;
}}
.stTextArea textarea:focus {{
    border-color: {acc} !important;
    box-shadow: 0 0 0 3px {acc_bg} !important;
    outline: none !important;
}}
.stTextArea textarea::placeholder {{ color: {text3} !important; }}

/* ── Buttons ── */
.stButton > button[kind="primary"] {{
    background: {acc} !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.6rem 1.25rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 3px rgba(99,102,241,0.3) !important;
    letter-spacing: 0.01em !important;
}}
.stButton > button[kind="primary"]:hover {{
    filter: brightness(1.1) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.45) !important;
}}
.stButton > button[kind="primary"]:active {{ transform: translateY(0) !important; }}
.stButton > button[kind="secondary"] {{
    background: {bg2} !important;
    color: {text} !important;
    border: 1.5px solid {border} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    padding: 0.5rem 1rem !important;
    transition: all 0.15s ease !important;
}}
.stButton > button[kind="secondary"]:hover {{
    background: {bg3} !important;
    border-color: {border2} !important;
    transform: translateY(-1px) !important;
}}
.stButton > button:disabled {{
    opacity: 0.45 !important;
    cursor: not-allowed !important;
    transform: none !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {bg2} !important;
    border-bottom: 2px solid {border} !important;
    padding: 0.35rem 0.35rem 0 !important;
    gap: 2px !important;
    border-radius: 10px 10px 0 0 !important;
}}
.stTabs [data-baseweb="tab"] {{
    background: transparent !important;
    color: {text2} !important;
    border: none !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0.55rem 1.1rem !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.15s ease !important;
    margin-bottom: -2px !important;
}}
.stTabs [aria-selected="true"] {{
    background: {bg} !important;
    color: {acc_txt} !important;
    border-bottom: 2px solid {acc} !important;
    font-weight: 700 !important;
}}
.stTabs [data-baseweb="tab"]:hover:not([aria-selected="true"]) {{
    background: {bg3} !important;
    color: {text} !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ background: {bg} !important; padding-top: 1.5rem !important; }}

/* ── Selectbox ── */
.stSelectbox > div > div {{
    background: {bg2} !important;
    border: 1.5px solid {border} !important;
    border-radius: 8px !important;
    color: {text} !important;
}}
.stSelectbox svg {{ fill: {text2} !important; }}

/* ── Expanders ── */
.stExpander {{
    border: 1.5px solid {border} !important;
    border-radius: 10px !important;
    background: {bg} !important;
    overflow: hidden !important;
}}
.stExpander summary {{
    background: {bg2} !important;
    padding: 0.75rem 1rem !important;
    color: {text} !important;
}}
.stExpander summary:hover {{ background: {bg3} !important; }}
div[data-testid="stExpanderDetails"] {{
    background: {bg} !important;
    padding: 1rem !important;
}}

/* ── Code blocks ── */
.stCodeBlock {{
    border: 1.5px solid {border} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}
.stCodeBlock pre, .stCodeBlock code {{
    background: {code_bg} !important;
    color: {text} !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace !important;
    font-size: 0.82rem !important;
    line-height: 1.65 !important;
}}

/* ── File uploader ── */
.stFileUploader > div {{
    background: {bg2} !important;
    border: 2px dashed {border} !important;
    border-radius: 10px !important;
    transition: border-color 0.15s ease !important;
}}
.stFileUploader > div:hover {{ border-color: {acc} !important; }}

/* ── Toggle / checkbox ── */
.stCheckbox label, .stToggle label {{ color: {text} !important; }}

/* ── Caption ── */
.stCaption, .stCaption p {{ color: {text3} !important; font-size: 0.78rem !important; }}

/* ── Markdown ── */
.stMarkdown p, .stMarkdown li {{ color: {text} !important; line-height: 1.65 !important; }}
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{ color: {text} !important; font-weight: 700 !important; }}
.stMarkdown a {{ color: {acc} !important; }}
.stMarkdown code {{ background: {bg3} !important; color: {text} !important; border-radius: 4px; padding: 1px 5px; font-size: 0.85em; }}

/* ── Alerts ── */
div[data-testid="stAlert"] {{ border-radius: 10px !important; border: none !important; }}

/* ── Spinner ── */
.stSpinner > div > div {{ border-top-color: {acc} !important; }}

/* ── Input text ── */
.stTextInput input {{
    background: {bg2} !important;
    color: {text} !important;
    border: 1.5px solid {border} !important;
    border-radius: 8px !important;
}}
.stTextInput input:focus {{ border-color: {acc} !important; outline: none !important; }}

/* ── Dividers ── */
hr {{ border-color: {border} !important; margin: 1.5rem 0 !important; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden !important; }}

/* ── Custom components ── */

.app-header {{
    padding: 1.5rem 0 1.25rem;
    border-bottom: 1px solid {border};
    margin-bottom: 1.75rem;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 1rem;
}}
.app-title {{
    font-size: 1.6rem;
    font-weight: 800;
    color: {text};
    letter-spacing: -0.04em;
    line-height: 1.1;
    margin: 0;
}}
.app-subtitle {{
    font-size: 0.875rem;
    color: {text2};
    margin: 0.3rem 0 0;
    line-height: 1.4;
}}

.section-label {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {text3};
    margin: 0 0 0.5rem;
    display: block;
}}

.tip-card {{
    background: {tip_bg};
    border: 1px solid {tip_brd};
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 1rem 0;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}}
.tip-card:hover {{ transform: translateY(-2px); box-shadow: {sh_md}; }}
.tip-card-tag {{
    display: inline-block;
    font-size: 0.63rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {acc_txt};
    background: {tip_tag};
    padding: 2px 8px;
    border-radius: 999px;
    margin-bottom: 0.4rem;
}}
.tip-card-title {{
    font-size: 0.875rem;
    font-weight: 700;
    color: {tip_ttl};
    margin: 0 0 0.3rem;
}}
.tip-card-body {{
    font-size: 0.81rem;
    color: {tip_bod};
    line-height: 1.55;
    margin: 0;
}}

.stat-card {{
    background: {bg2};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0.875rem 1rem;
    text-align: center;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}}
.stat-card:hover {{ transform: translateY(-2px); box-shadow: {sh_md}; }}
.stat-value {{ font-size: 1.45rem; font-weight: 800; color: {text}; line-height: 1.15; letter-spacing: -0.03em; }}
.stat-delta-good {{ color: {succ}; font-size: 0.75rem; font-weight: 600; display: block; }}
.stat-delta-none {{ color: {text3}; font-size: 0.75rem; display: block; }}
.stat-label {{ font-size: 0.7rem; color: {text2}; margin-top: 0.25rem; }}

.status-pill {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.03em;
}}
.status-ai   {{ background: {succ_bg}; color: {succ}; border: 1px solid {succ_bg}; }}
.status-rule {{ background: {warn_bg}; color: {warn}; border: 1px solid {warn_bg}; }}
.status-off  {{ background: {bg3};    color: {text2}; border: 1px solid {border}; }}

.mode-badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.66rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.mode-small  {{ background: {'#1e3a5f' if dark else '#dbeafe'}; color: {'#93c5fd' if dark else '#1d4ed8'}; }}
.mode-medium {{ background: {warn_bg}; color: {warn}; }}
.mode-large  {{ background: {succ_bg}; color: {succ}; }}
.mode-ai     {{ background: {'#2d1b69' if dark else '#f3e8ff'}; color: {'#c4b5fd' if dark else '#7c3aed'}; }}

.install-box {{
    background: {warn_bg};
    border: 1px solid {'rgba(252,211,77,0.2)' if dark else '#fde68a'};
    border-radius: 8px;
    padding: 0.75rem 1rem;
    font-size: 0.81rem;
    color: {warn};
    margin-bottom: 1rem;
}}

.empty-state {{
    padding: 3rem 1rem 2rem;
    text-align: center;
    border: 2px dashed {border};
    border-radius: 14px;
    background: {bg2};
    margin-top: 0.5rem;
}}
.empty-state-icon {{ font-size: 2.25rem; display: block; margin-bottom: 0.75rem; }}
.empty-state-title {{ font-size: 1rem; font-weight: 700; color: {text}; margin-bottom: 0.4rem; }}
.empty-state-body  {{ font-size: 0.83rem; color: {text2}; line-height: 1.6; max-width: 400px; margin: 0 auto; }}

.insight-card {{
    background: {bg2};
    border: 1px solid {border};
    border-left: 3px solid {acc};
    border-radius: 0 8px 8px 0;
    padding: 0.7rem 1rem;
    margin: 0.35rem 0;
    transition: transform 0.15s ease;
}}
.insight-card:hover {{ transform: translateX(3px); }}
.insight-category {{
    font-size: 0.64rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: {acc_txt};
    margin-bottom: 0.2rem;
}}
.insight-change {{ font-size: 0.83rem; font-weight: 600; color: {text}; margin-bottom: 0.15rem; }}
.insight-why {{ font-size: 0.77rem; color: {text2}; line-height: 1.45; }}

.learn-card {{
    background: {bg2};
    border: 1.5px solid {border};
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
    cursor: pointer;
}}
.learn-card:hover {{ border-color: {acc}; box-shadow: {sh_md}; transform: translateY(-2px); }}
.learn-card-icon {{ font-size: 1.6rem; display: block; margin-bottom: 0.6rem; }}
.learn-card-title {{ font-size: 0.9rem; font-weight: 700; color: {text}; margin-bottom: 0.35rem; }}
.learn-card-meta {{ font-size: 0.7rem; color: {text2}; margin-bottom: 0.6rem; display: flex; gap: 0.75rem; align-items: center; flex-wrap: wrap; }}
.learn-card-summary {{ font-size: 0.82rem; color: {text2}; line-height: 1.55; }}

.difficulty-badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.62rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}}
.diff-Beginner     {{ background: {succ_bg}; color: {succ}; }}
.diff-Intermediate {{ background: {warn_bg}; color: {warn}; }}
.diff-Advanced     {{ background: {'#1e3a5f' if dark else '#dbeafe'}; color: {'#93c5fd' if dark else '#1d4ed8'}; }}

.platform-badge {{
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    background: {acc_bg};
    color: {acc_txt};
    border: 1px solid {'rgba(99,102,241,0.3)' if dark else '#c7d2fe'};
    margin-bottom: 1rem;
    display: inline-block;
}}

.onboarding-hint {{
    background: {bg2};
    border: 1.5px dashed {border};
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin: 0.5rem 0;
    font-size: 0.81rem;
    color: {text2};
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    line-height: 1.5;
}}
.hint-icon {{ flex-shrink: 0; font-size: 1rem; margin-top: 1px; }}

.app-footer {{
    border-top: 1px solid {border};
    padding: 1.5rem 0;
    margin-top: 3.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}}
.footer-text {{ font-size: 0.78rem; color: {text2}; }}
.footer-link {{ color: {acc}; text-decoration: none; font-weight: 500; }}
.footer-link:hover {{ text-decoration: underline; }}

/* Skeleton shimmer */
.skeleton {{
    background: linear-gradient(90deg, {bg3} 25%, {bg2} 50%, {bg3} 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s infinite;
    border-radius: 6px;
    margin: 5px 0;
}}
@keyframes shimmer {{
    0% {{ background-position: 200% 0; }}
    100% {{ background-position: -200% 0; }}
}}
</style>
"""


# ── Cached resources ──────────────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading optimizer…")
def _get_optimizer():
    return PromptOptimizer()

@st.cache_resource(show_spinner=False)
def _get_extractor():
    return FileExtractor()

@st.cache_data(ttl=10, show_spinner=False)
def _cached_models():
    return get_available_models()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

def _fmt(n: int) -> str:
    return f"{n:,}"

def _mode_badge(mode: str) -> str:
    return f'<span class="mode-badge mode-{mode}">{mode}</span>'

_PLATFORM_META = {
    "Claude":           ("🟣", "Anthropic"),
    "ChatGPT":          ("🟢", "OpenAI"),
    "Gemini":           ("🔵", "Google"),
    "Cursor":           ("⬛", "Code IDE"),
    "Windsurf":         ("🟤", "Code IDE"),
    "Lovable":          ("🩷", "Full-stack"),
    "Bolt":             ("⚡", "Full-stack"),
    "Replit Agent":     ("🟠", "Agent"),
    "Manus":            ("🤖", "Agent"),
    "Perplexity":       ("🔍", "Research"),
    "Midjourney":       ("🎨", "Image"),
    "Flux":             ("🎨", "Image"),
    "Stable Diffusion": ("🎨", "Image"),
}


# ── Reusable HTML components ──────────────────────────────────────────────────

def _tip_card(tip: dict) -> str:
    return f"""
<div class="tip-card">
  <div class="tip-card-tag">{tip['icon']} {tip['type']}</div>
  <div class="tip-card-title">{tip['title']}</div>
  <p class="tip-card-body">{tip['body']}</p>
</div>"""

def _stat_card(value: str, label: str, delta: str = "", delta_good: bool = True) -> str:
    delta_cls = "stat-delta-good" if delta_good else "stat-delta-none"
    delta_html = f'<span class="{delta_cls}">{delta}</span>' if delta else ""
    return f"""
<div class="stat-card">
  <div class="stat-value">{value}</div>
  {delta_html}
  <div class="stat-label">{label}</div>
</div>"""

def _insight_card(insight: dict) -> str:
    return f"""
<div class="insight-card">
  <div class="insight-category">{insight['icon']} {insight['category']}</div>
  <div class="insight-change">{insight['change']}</div>
  <div class="insight-why">{insight['why']}</div>
</div>"""

def _empty_state(icon: str, title: str, body: str) -> str:
    return f"""
<div class="empty-state">
  <span class="empty-state-icon">{icon}</span>
  <div class="empty-state-title">{title}</div>
  <p class="empty-state-body">{body}</p>
</div>"""

def _hint(text: str, icon: str = "💡") -> str:
    return f'<div class="onboarding-hint"><span class="hint-icon">{icon}</span>{text}</div>'


# ── Sidebar ───────────────────────────────────────────────────────────────────

def render_sidebar():
    with st.sidebar:
        # Dark mode toggle at top
        dark = st.session_state.get("dark_mode", False)
        new_dark = st.toggle("Dark mode", value=dark, key="theme_toggle")
        if new_dark != dark:
            st.session_state.dark_mode = new_dark
            st.rerun()

        st.markdown("---")
        st.markdown("### ⚙️ Engine")

        groq_key_val = _groq_key()
        has_auto_groq = bool(groq_key_val)

        if has_auto_groq:
            st.markdown('<div class="status-pill status-ai">🟢 Groq AI connected</div>', unsafe_allow_html=True)
            use_groq = st.toggle("Use Groq AI (cloud)", value=True)
            groq_model = st.selectbox("Groq model", GROQ_MODELS, index=0)
            if use_groq:
                st.caption(f"Using **{groq_model}** via Groq cloud.")
                st.markdown("---")
                st.caption("💡 Groq runs inference at ~500 tok/s — typically under 3s per optimization.")
                return True, "groq", groq_model
        else:
            with st.expander("🔑 Connect Groq AI (free)"):
                manual_key = st.text_input("Groq API key", type="password", placeholder="gsk_…")
                st.caption("Free key at [console.groq.com](https://console.groq.com)")
                if manual_key:
                    groq_model = st.selectbox("Model", GROQ_MODELS, index=0)
                    st.session_state["_manual_groq"] = manual_key
                    return True, "groq", groq_model

        models = _cached_models()
        if models:
            default_model = _pick_default_model(models)
            default_idx = models.index(default_model) if default_model in models else 0
            st.markdown('<div class="status-pill status-ai">🟢 Ollama connected</div>', unsafe_allow_html=True)
            use_llm = st.toggle("Use AI (Ollama local)", value=not has_auto_groq)
            model = st.selectbox("Ollama model", models, index=default_idx)
            if use_llm:
                st.caption(f"Using **{model}** via local Ollama.")
                return True, "ollama", model

        if not has_auto_groq and not models:
            st.markdown('<div class="status-pill status-off">⚪ No AI backend</div>', unsafe_allow_html=True)
            st.markdown(
                "**Option 1 — Groq (recommended):**\n\nFree key at [console.groq.com](https://console.groq.com)\n\n"
                "**Option 2 — Ollama (local):**\n\n1. [Download Ollama](https://ollama.com/download)\n2. `ollama pull llama3.2`\n3. Refresh"
            )

        st.markdown("---")
        st.caption("Rule-based optimizer active (no AI backend).")
        return False, None, None


# ── Optimizer Tab ─────────────────────────────────────────────────────────────

def render_optimizer_tab(use_llm: bool, backend: str, model: str, groq_key_val: str):
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<span class="section-label">Input Prompt</span>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload file", type=["pdf", "docx", "txt", "md"],
            label_visibility="collapsed",
            help="Upload a PDF, Word document, or text file to extract its text.",
        )
        prefill = ""
        if uploaded is not None:
            fk = f"file_{uploaded.name}_{uploaded.size}"
            if st.session_state.get("_last_file") != fk:
                with st.spinner(f"Extracting text from {uploaded.name}…"):
                    prefill = _get_extractor().extract(uploaded)
                st.session_state["_last_file"] = fk
                st.session_state["_prefill"] = prefill
            else:
                prefill = st.session_state.get("_prefill", "")

        # First-time hint
        if not st.session_state.get("_used_optimizer"):
            example = get_empty_state_example()
            st.markdown(
                _hint(f"New here? Try pasting a prompt and hitting Optimize. Example: <em>\"{example[:80]}…\"</em>", "👋"),
                unsafe_allow_html=True,
            )

        user_input = st.text_area(
            "Paste your prompt", value=prefill, height=400,
            placeholder=(
                "Paste your prompt here…\n\n"
                "Examples:\n"
                "• Claude / Cursor / Windsurf system prompts\n"
                "• ChatGPT or Gemini prompts\n"
                "• PRDs, meeting notes, research briefs\n"
                "• Marketing copy, emails, outlines"
            ),
            label_visibility="collapsed",
        )

        char_count = len(user_input)
        tok_est = char_count // 4
        st.caption(f"{_fmt(char_count)} chars · ~{_fmt(tok_est)} tokens")

        if char_count > 6000:
            st.markdown(
                _hint("Large prompt detected. After optimizing, export as Markdown and paste into a fresh conversation to reduce context usage.", "📄"),
                unsafe_allow_html=True,
            )

        btn_label = "⚡ Optimize with AI" if use_llm else "⚡ Optimize Prompt"
        optimize_clicked = st.button(
            btn_label, type="primary", use_container_width=True,
            disabled=not user_input.strip(),
        )

    with right:
        st.markdown('<span class="section-label">Optimized Prompt</span>', unsafe_allow_html=True)

        if optimize_clicked and user_input.strip():
            st.session_state["_used_optimizer"] = True
            t0 = time.perf_counter()
            optimized_text = None
            used_llm = False
            result = None

            if use_llm and model:
                msg = (
                    f"Running 6-pass AI optimization via Groq ({model})…"
                    if backend == "groq"
                    else f"Running 6-pass AI optimization with {model}…"
                )
                with st.spinner(msg):
                    key_to_use = groq_key_val or st.session_state.get("_manual_groq", "")
                    if backend == "groq":
                        optimized_text = optimize_with_groq(user_input, key_to_use, model)
                    else:
                        optimized_text = optimize_with_llm(user_input, model)
                    if optimized_text:
                        used_llm = True

            if not optimized_text:
                with st.spinner("Running 6-pass rule-based optimization…"):
                    result = _get_optimizer().optimize(user_input)
                    optimized_text = result["optimized"]

            elapsed = time.perf_counter() - t0
            insights = analyze_changes(user_input, optimized_text)

            st.session_state.update({
                "result_text":    optimized_text,
                "original":       user_input,
                "elapsed":        elapsed,
                "used_llm":       used_llm,
                "llm_model":      model if used_llm else None,
                "rule_mode":      result["mode"] if result else None,
                "warnings":       result["warnings"] if result else [],
                "score":          result["score"] if result else None,
                "impossible":     result.get("impossible_fixes", []) if result else [],
                "contradictions": result.get("contradictions", []) if result else [],
                "insights":       insights,
            })

        if "result_text" in st.session_state:
            optimized_text = st.session_state["result_text"]
            original       = st.session_state["original"]
            elapsed        = st.session_state.get("elapsed", 0)
            used_llm       = st.session_state.get("used_llm", False)
            llm_model      = st.session_state.get("llm_model") or ""
            rule_mode      = st.session_state.get("rule_mode") or "medium"
            insights       = st.session_state.get("insights", [])

            if used_llm:
                pill = f'<span class="status-pill status-ai">🤖 AI optimized</span>'
                meta = f'<span style="font-size:0.78rem;color:#6b7280;">{llm_model} · {elapsed:.1f}s</span>'
            else:
                badge = _mode_badge(rule_mode)
                pill  = f'<span class="status-pill status-rule">⚡ Rule-based</span>'
                meta  = f'{badge} <span style="font-size:0.78rem;color:#6b7280;">{elapsed:.2f}s</span>'

            st.markdown(f'{pill} &nbsp; {meta}', unsafe_allow_html=True)

            # Impossible requirements
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

            # Optimization insights
            if insights:
                with st.expander("🔍 What changed & why", expanded=True):
                    for ins in insights:
                        st.markdown(_insight_card(ins), unsafe_allow_html=True)

            # Output
            st.code(optimized_text, language="markdown")

            dl1, dl2, dl3 = st.columns(3)
            with dl1:
                st.download_button(
                    "⬇ TXT", data=optimized_text,
                    file_name="optimized_prompt.txt", mime="text/plain",
                    use_container_width=True,
                )
            with dl2:
                st.download_button(
                    "⬇ Markdown", data=optimized_text,
                    file_name="optimized_prompt.md", mime="text/markdown",
                    use_container_width=True,
                )
            with dl3:
                escaped = optimized_text.replace("\\", "\\\\").replace("`", "\\`")
                _copy_html = (
                    f"<button onclick=\"navigator.clipboard.writeText(`{escaped}`)"
                    ".then(()=>{this.textContent='✓ Copied!';setTimeout(()=>this.textContent='📋 Copy',2000)})"
                    ".catch(()=>this.textContent='⚠ Failed')\" "
                    "style=\"width:100%;padding:0.55rem 0.5rem;background:#6366f1;color:#fff;"
                    "border:none;border-radius:8px;cursor:pointer;font-size:0.875rem;"
                    "font-weight:600;letter-spacing:0.01em;\">📋 Copy</button>"
                )
                if _HAS_IFRAME:
                    _st_iframe(_copy_html, height=44)
                else:
                    _components.html(_copy_html, height=44)

            st.markdown('<hr style="margin:1.25rem 0;border-color:var(--border,#e5e7eb);">', unsafe_allow_html=True)

            # Stats
            st.markdown('<span class="section-label">Statistics</span>', unsafe_allow_html=True)
            stats = calculate_stats(original, optimized_text)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(_stat_card(_fmt(stats["original_chars"]), "Original chars"), unsafe_allow_html=True)
            with c2:
                st.markdown(_stat_card(_fmt(stats["optimized_chars"]), "Optimized chars"), unsafe_allow_html=True)
            with c3:
                removed = stats["chars_removed"]
                sign = "-" if removed >= 0 else "+"
                st.markdown(_stat_card(f"{sign}{_fmt(abs(removed))}", "Chars removed"), unsafe_allow_html=True)
            with c4:
                pct = stats["reduction_pct"]
                st.markdown(_stat_card(f"{pct:.1f}%", "Char reduction", f"{'↓' if pct > 0 else '—'} reduction", pct > 0), unsafe_allow_html=True)
            with c5:
                t_pct = stats["token_reduction_pct"]
                t_removed = stats["token_reduction"]
                st.markdown(_stat_card(f"{t_pct:.1f}%", "Token reduction", f"~{_fmt(abs(t_removed))} tokens saved", t_pct > 0), unsafe_allow_html=True)

            # Quality score (rule-based only)
            score = st.session_state.get("score")
            if score and not used_llm:
                st.markdown('<hr style="margin:1.25rem 0;border-color:var(--border,#e5e7eb);">', unsafe_allow_html=True)
                st.markdown('<span class="section-label">Quality Score</span>', unsafe_allow_html=True)
                grade_colors = {"A": "#059669", "B": "#2563eb", "C": "#d97706", "D": "#dc2626", "F": "#7f1d1d"}
                gc = grade_colors.get(score.get("grade", "F"), "#6b7280")
                st.markdown(
                    f'<div style="font-size:1.8rem;font-weight:800;color:{gc};letter-spacing:-0.04em;">'
                    f'{score.get("overall",0)}/100 '
                    f'<span style="font-size:1.1rem;">{score.get("grade","?")}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                dims = [
                    ("Clarity", "clarity"), ("Specificity", "specificity"),
                    ("Hallucination Resist.", "hallucination_resistance"),
                    ("Research Quality", "research_quality"),
                    ("Output Structure", "output_structure"),
                    ("Token Efficiency", "token_efficiency"),
                    ("Contradiction Score", "contradiction_score"),
                    ("Impossible Req.", "impossible_requirement_score"),
                ]
                cols = st.columns(4)
                for i, (label, key) in enumerate(dims):
                    val = score.get(key, 0)
                    c_col = "#059669" if val >= 8 else "#d97706" if val >= 5 else "#dc2626"
                    with cols[i % 4]:
                        st.markdown(
                            f'<div class="stat-card">'
                            f'<div class="stat-value" style="font-size:1.15rem;color:{c_col};">{val}/10</div>'
                            f'<div class="stat-label">{label}</div></div>',
                            unsafe_allow_html=True,
                        )

            # Contextual tip after result
            tip = get_contextual_tip("after_optimize")
            st.markdown(_tip_card(tip), unsafe_allow_html=True)

        else:
            # Empty state
            st.markdown(
                _empty_state(
                    "✨",
                    "Your optimized prompt will appear here",
                    "Paste any prompt on the left and click Optimize. The optimizer runs up to 6 passes — improving clarity, structure, constraints, and token efficiency.",
                ),
                unsafe_allow_html=True,
            )
            tip = get_contextual_tip("always")
            st.markdown(_tip_card(tip), unsafe_allow_html=True)


# ── Architect Tab ─────────────────────────────────────────────────────────────

def render_architect_tab(use_llm: bool, backend: str, model: str, groq_key_val: str):
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<span class="section-label">Target Platform</span>', unsafe_allow_html=True)
        platform = st.selectbox(
            "Platform", PLATFORMS,
            format_func=lambda p: f"{_PLATFORM_META[p][0]}  {p}  ·  {_PLATFORM_META[p][1]}",
            label_visibility="collapsed",
        )
        icon, category = _PLATFORM_META[platform]
        st.markdown(
            f'<div class="platform-badge">{icon} {platform} &nbsp;·&nbsp; {category}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<span class="section-label">Your Request</span>', unsafe_allow_html=True)

        # Platform tip
        ctx_tip = get_contextual_tip(f"architect_{platform}", platform)
        st.markdown(_tip_card(ctx_tip), unsafe_allow_html=True)

        user_request = st.text_area(
            "Describe what you want", height=280,
            placeholder=(
                "Describe your goal in plain language — any detail level.\n\n"
                "Examples:\n"
                "• Build a SaaS landing page with waitlist signup\n"
                "• Write a market research report on AI coding tools\n"
                "• Create a cyberpunk cityscape at dusk, neon-lit rain\n"
                "• Build an e-commerce app with Stripe and auth"
            ),
            label_visibility="collapsed",
        )
        if user_request:
            st.caption(f"{_fmt(len(user_request))} chars · ~{_fmt(len(user_request)//4)} tokens")

        if not use_llm:
            st.markdown(
                '<div class="install-box">⚠️ PromptArchitect requires an AI backend. Connect Groq or Ollama in the sidebar.</div>',
                unsafe_allow_html=True,
            )

        generate_clicked = st.button(
            "🏗️ Architect Prompt", type="primary", use_container_width=True,
            disabled=not user_request.strip() or not use_llm,
            key="arch_generate",
        )

    with right:
        st.markdown('<span class="section-label">Generated Prompt</span>', unsafe_allow_html=True)

        if generate_clicked and user_request.strip() and use_llm:
            t0 = time.perf_counter()
            spinner_msg = f"Running 7-phase architecture for {platform} via {'Groq' if backend == 'groq' else 'Ollama'}…"
            with st.spinner(spinner_msg):
                key_to_use = groq_key_val or st.session_state.get("_manual_groq", "")
                raw = (
                    architect_with_groq(user_request, platform, key_to_use, model)
                    if backend == "groq"
                    else architect_with_ollama(user_request, platform, model)
                )
            elapsed = time.perf_counter() - t0
            if raw:
                parsed = parse_architect_output(raw)
                st.session_state.update({
                    "arch_result":   parsed,
                    "arch_platform": platform,
                    "arch_model":    model,
                    "arch_elapsed":  elapsed,
                })
            else:
                st.error("Architecture failed — check your backend connection and try again.")

        if "arch_result" in st.session_state:
            parsed    = st.session_state["arch_result"]
            plat      = st.session_state.get("arch_platform", "")
            arch_mdl  = st.session_state.get("arch_model", "")
            arch_sec  = st.session_state.get("arch_elapsed", 0.0)
            icon_p, _ = _PLATFORM_META.get(plat, ("🤖", ""))

            st.markdown(
                f'<span class="status-pill status-ai">{icon_p} Optimized for {plat}</span>'
                f'&nbsp;<span style="font-size:0.78rem;color:#6b7280;">{arch_mdl} · {arch_sec:.1f}s</span>',
                unsafe_allow_html=True,
            )

            if parsed["analysis"]:
                with st.expander("📊 Prompt Analysis", expanded=True):
                    st.markdown(parsed["analysis"])

            st.markdown('<span class="section-label" style="margin-top:0.75rem;">Optimized Prompt</span>', unsafe_allow_html=True)
            st.code(parsed["prompt"], language="markdown")

            safe_name = plat.lower().replace(" ", "_")
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button(
                    "⬇ Download TXT", data=parsed["prompt"],
                    file_name=f"prompt_{safe_name}.txt", mime="text/plain",
                    use_container_width=True, key="arch_dl_txt",
                )
            with dl2:
                st.download_button(
                    "⬇ Download Markdown", data=parsed["prompt"],
                    file_name=f"prompt_{safe_name}.md", mime="text/markdown",
                    use_container_width=True, key="arch_dl_md",
                )

            if parsed["enhancements"]:
                with st.expander("✨ Enhancements Applied"):
                    st.markdown(parsed["enhancements"])

            if parsed.get("quality_score"):
                with st.expander("🏆 Quality Score", expanded=True):
                    qs = parse_quality_score(parsed["quality_score"])
                    total = qs["total"]
                    total_color = "#059669" if total >= 95 else "#d97706" if total >= 80 else "#dc2626"
                    st.markdown(
                        f'<div style="font-size:1.8rem;font-weight:800;color:{total_color};letter-spacing:-0.04em;margin-bottom:0.75rem;">'
                        f'{total}/100'
                        f'<span style="font-size:0.85rem;color:#6b7280;font-weight:400;margin-left:0.75rem;">'
                        f'{"✅ Target reached" if total >= 95 else "⚠️ Below 95 target"}</span></div>',
                        unsafe_allow_html=True,
                    )
                    if qs["scores"]:
                        cols = st.columns(5)
                        for i, (label, val) in enumerate(qs["scores"].items()):
                            c_col = "#059669" if val >= 9 else "#d97706" if val >= 7 else "#dc2626"
                            with cols[i % 5]:
                                st.markdown(
                                    f'<div class="stat-card">'
                                    f'<div class="stat-value" style="font-size:1.1rem;color:{c_col};">{val}/10</div>'
                                    f'<div class="stat-label">{label}</div></div>',
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.markdown(parsed["quality_score"])

            st.markdown(
                _hint("Markdown exports work great in Claude Projects — upload to a fresh project for long-form workflows.", "📄"),
                unsafe_allow_html=True,
            )

        else:
            st.markdown(
                _empty_state(
                    "🏗️",
                    "Your production-grade prompt will appear here",
                    "Select a target platform, describe your goal, and click Architect Prompt. The 7-phase pipeline generates prompts optimized for that specific AI model.",
                ),
                unsafe_allow_html=True,
            )


# ── Learn Tab ─────────────────────────────────────────────────────────────────

def render_learn_tab():
    st.markdown(
        '<p style="font-size:0.95rem;color:#6b7280;margin-bottom:1.5rem;">'
        'Learn prompt engineering techniques, platform best practices, and workflow patterns '
        'that make your prompts significantly more effective.'
        '</p>',
        unsafe_allow_html=True,
    )

    categories = list(LEARNING_CONTENT.keys())
    selected_cat = st.session_state.get("learn_cat", "Basics")

    # Category pills (horizontal radio group)
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories):
        with cols[i]:
            if st.button(
                cat,
                key=f"cat_{cat}",
                type="primary" if cat == selected_cat else "secondary",
                use_container_width=True,
            ):
                st.session_state["learn_cat"] = cat
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    items = LEARNING_CONTENT.get(selected_cat, [])
    if not items:
        st.markdown(
            _empty_state("📚", "Coming soon", "More content for this category is on the way."),
            unsafe_allow_html=True,
        )
        return

    for item in items:
        diff_cls = f"diff-{item['difficulty']}"
        card_header = f"""
<div class="learn-card">
  <span class="learn-card-icon">{item['icon']}</span>
  <div class="learn-card-title">{item['title']}</div>
  <div class="learn-card-meta">
    <span class="difficulty-badge {diff_cls}">{item['difficulty']}</span>
    <span>📖 {item['read_time']}</span>
  </div>
  <div class="learn-card-summary">{item['summary']}</div>
</div>"""
        with st.expander(f"{item['icon']} {item['title']}"):
            st.markdown(f"*{item['summary']}*")
            st.markdown(
                f'<span class="difficulty-badge {diff_cls}">{item["difficulty"]}</span> &nbsp; 📖 {item["read_time"]}',
                unsafe_allow_html=True,
            )
            st.markdown("**Key takeaways:**")
            for point in item["key_points"]:
                st.markdown(f"- {point}")

    # Rotating tips at the bottom of learn tab
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="section-label">Quick Tips</span>', unsafe_allow_html=True)
    tips = get_rotating_tips(3)
    t1, t2, t3 = st.columns(3)
    for col, tip in zip([t1, t2, t3], tips):
        with col:
            st.markdown(_tip_card(tip), unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────

def _render_footer():
    st.markdown(
        """
<div class="app-footer">
  <div class="footer-text">
    Feedback, suggestions, or bug reports:&nbsp;
    <a href="mailto:tanmayagr2021@gmail.com" class="footer-link">tanmayagr2021@gmail.com</a>
  </div>
  <div class="footer-text">
    Prompt Optimizer &nbsp;·&nbsp; Built with Streamlit
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    dark = st.session_state.get("dark_mode", False)
    st.markdown(_css(dark), unsafe_allow_html=True)

    st.markdown(
        '<div class="app-header">'
        '<div>'
        '<p class="app-title">⚡ Prompt Optimizer</p>'
        '<p class="app-subtitle">Optimize prompts · Architect for any AI platform · Learn prompt engineering</p>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    use_llm, backend, model = render_sidebar()
    groq_key_val = _groq_key() or st.session_state.get("_manual_groq", "")

    tab1, tab2, tab3 = st.tabs(["⚡ Optimizer", "🏗️ Architect", "📚 Learn"])

    with tab1:
        render_optimizer_tab(use_llm, backend, model, groq_key_val)
    with tab2:
        render_architect_tab(use_llm, backend, model, groq_key_val)
    with tab3:
        render_learn_tab()

    _render_footer()


if __name__ == "__main__":
    main()
