"""
Prompt Optimizer — Streamlit application entry point.
Run with: streamlit run app.py
"""

import os
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
    parse_quality_score,
)
from utils import calculate_stats

st.set_page_config(
    page_title="Prompt Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif; }
#MainMenu { visibility: hidden; }
footer   { visibility: hidden; }
header   { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
.app-title    { font-size: 2rem; font-weight: 700; letter-spacing: -0.5px; margin-bottom: 0; }
.app-subtitle { color: #6b7280; font-size: 0.95rem; margin-top: 0.25rem; margin-bottom: 1.5rem; }
.section-label { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.08em; color: #6b7280; margin-bottom: 0.4rem; }
.status-pill { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 600; margin-bottom: 1rem; }
.status-ai   { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
.status-rule { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
.status-off  { background: #f3f4f6; color: #6b7280; border: 1px solid #e5e7eb; }
.mode-badge { display: inline-block; padding: 2px 10px; border-radius: 999px; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }
.mode-small  { background: #dbeafe; color: #1d4ed8; }
.mode-medium { background: #fef3c7; color: #b45309; }
.mode-large  { background: #dcfce7; color: #15803d; }
.mode-ai     { background: #f3e8ff; color: #7c3aed; }
.stat-card  { background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; padding: 0.75rem 1rem; text-align: center; }
.stat-value { font-size: 1.5rem; font-weight: 700; color: #111827; line-height: 1.2; }
.stat-delta-good { color: #059669; font-size: 0.8rem; font-weight: 600; }
.stat-delta-none { color: #6b7280; font-size: 0.8rem; }
.stat-label      { font-size: 0.75rem; color: #6b7280; margin-top: 0.2rem; }
.divider { border: none; border-top: 1px solid #e5e7eb; margin: 1.5rem 0; }
.install-box { background: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 0.75rem 1rem; font-size: 0.85rem; color: #92400e; margin-bottom: 1rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading rule-based optimizer…")
def get_optimizer():
    return PromptOptimizer()

@st.cache_resource(show_spinner=False)
def get_extractor():
    return FileExtractor()

@st.cache_data(ttl=10, show_spinner=False)
def _cached_models():
    return get_available_models()

def _get_groq_key():
    try:
        return st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        return os.environ.get("GROQ_API_KEY", "")

def _mode_badge(mode, use_llm):
    if use_llm:
        return '<span class="mode-badge mode-ai">AI</span>'
    return f'<span class="mode-badge mode-{mode}">{mode}</span>'

def _format_number(n):
    return f"{n:,}"


def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Optimization Engine")
        auto_groq_key = _get_groq_key()
        has_groq_auto = bool(auto_groq_key)

        if has_groq_auto:
            st.markdown('<div class="status-pill status-ai">🟢 Groq AI connected</div>', unsafe_allow_html=True)
            use_groq = st.toggle("Use Groq AI (cloud)", value=True)
            groq_model = st.selectbox("Groq model", GROQ_MODELS, index=0)
            if use_groq:
                st.caption(f"Using **{groq_model}** via Groq cloud API.")
                return True, "groq", groq_model
        else:
            with st.expander("🔑 Connect Groq AI (free cloud API)"):
                manual_key = st.text_input("Groq API key", type="password", placeholder="gsk_…")
                st.caption("Get a free key at [console.groq.com](https://console.groq.com)")
                if manual_key:
                    groq_model = st.selectbox("Groq model", GROQ_MODELS, index=0)
                    return True, "groq", groq_model

        models = _cached_models()
        has_ollama = bool(models)
        if has_ollama:
            default_model = _pick_default_model(models)
            default_idx = models.index(default_model) if default_model in models else 0
            st.markdown('<div class="status-pill status-ai">🟢 Ollama connected</div>', unsafe_allow_html=True)
            use_llm = st.toggle("Use AI (Ollama local)", value=not has_groq_auto)
            model = st.selectbox("Ollama model", models, index=default_idx)
            if use_llm:
                st.caption(f"Using **{model}** locally via Ollama.")
                return True, "ollama", model

        if not has_groq_auto and not has_ollama:
            st.markdown('<div class="status-pill status-off">⚪ No AI backend</div>', unsafe_allow_html=True)
            st.markdown(
                "**Option 1 — Groq (free cloud AI):**\n\nGet a free key at [console.groq.com](https://console.groq.com) and paste it above.\n\n"
                "**Option 2 — Ollama (local):**\n\n1. [Download Ollama](https://ollama.com/download)\n2. Run `ollama pull llama3.2`\n3. Refresh"
            )

        st.divider()
        st.caption("Using fast rule-based optimizer.")
        return False, None, None


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


def render_architect_tab(use_llm, backend, model, groq_key):
    left, right = st.columns([1, 1], gap="large")
    with left:
        st.markdown('<p class="section-label">Target Platform</p>', unsafe_allow_html=True)
        platform = st.selectbox(
            "Platform", PLATFORMS,
            format_func=lambda p: f"{_PLATFORM_META[p][0]}  {p}  ·  {_PLATFORM_META[p][1]}",
            label_visibility="collapsed",
        )
        icon, category = _PLATFORM_META[platform]
        st.markdown(
            f'<div style="margin-bottom:1rem;"><span style="background:#eef2ff;color:#4f46e5;'
            f'border:1px solid #c7d2fe;border-radius:999px;padding:4px 14px;font-size:0.8rem;font-weight:600;">'
            f'{icon} {platform} &nbsp;·&nbsp; {category}</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown('<p class="section-label">Your Request</p>', unsafe_allow_html=True)
        user_request = st.text_area(
            "Describe what you want", height=320,
            placeholder=(
                "Describe your goal in plain language — any length, any detail.\n\n"
                "Examples:\n• Build a SaaS landing page with waitlist signup\n"
                "• Write a market research report on AI coding tools\n"
                "• Create a cyberpunk cityscape at dusk, neon-lit rain\n"
                "• Build an e-commerce app with Stripe and auth"
            ),
            label_visibility="collapsed",
        )
        if user_request:
            st.caption(f"{_format_number(len(user_request))} characters · ~{_format_number(len(user_request)//4)} tokens")
        generate_clicked = st.button(
            "🏗️ Architect Prompt", type="primary", use_container_width=True,
            disabled=not user_request.strip() or not use_llm, key="arch_generate",
        )
        if not use_llm:
            st.markdown('<div class="install-box">⚠️ PromptArchitect requires an AI backend. Connect Groq or Ollama in the sidebar.</div>', unsafe_allow_html=True)

    with right:
        st.markdown('<p class="section-label">Generated Prompt</p>', unsafe_allow_html=True)
        if generate_clicked and user_request.strip() and use_llm:
            t0 = time.perf_counter()
            spinner_msg = f"Running 13-phase architecture for {platform} via {'Groq' if backend=='groq' else 'Ollama'}…"
            with st.spinner(spinner_msg):
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
            st.markdown(
                f'<span class="status-pill status-ai">{icon_p} Optimized for {plat}</span>'
                f'&nbsp;<span style="color:#6b7280;font-size:0.8rem;">{arch_mdl} · {arch_sec:.1f}s</span>',
                unsafe_allow_html=True,
            )
            if parsed["analysis"]:
                with st.expander("📊 Prompt Analysis", expanded=True):
                    st.markdown(parsed["analysis"])
            st.markdown('<p class="section-label" style="margin-top:0.5rem;">Optimized Prompt</p>', unsafe_allow_html=True)
            st.code(parsed["prompt"], language="markdown")
            safe_name = plat.lower().replace(" ", "_")
            dl1, dl2 = st.columns(2)
            with dl1:
                st.download_button("⬇ Download TXT", data=parsed["prompt"], file_name=f"prompt_{safe_name}.txt", mime="text/plain", use_container_width=True, key="arch_dl_txt")
            with dl2:
                st.download_button("⬇ Download Markdown", data=parsed["prompt"], file_name=f"prompt_{safe_name}.md", mime="text/markdown", use_container_width=True, key="arch_dl_md")
            if parsed["enhancements"]:
                with st.expander("✨ Enhancements Added"):
                    st.markdown(parsed["enhancements"])

            if parsed.get("quality_score"):
                with st.expander("🏆 Quality Score", expanded=True):
                    qs = parse_quality_score(parsed["quality_score"])
                    total = qs["total"]
                    total_color = "#15803d" if total >= 95 else "#b45309" if total >= 80 else "#dc2626"
                    st.markdown(
                        f'<div style="font-size:1.8rem;font-weight:700;color:{total_color};margin-bottom:0.75rem;">'
                        f'{total}/100'
                        f'<span style="font-size:0.9rem;color:#6b7280;font-weight:400;margin-left:0.75rem;">'
                        f'{"✅ Target reached" if total >= 95 else "⚠️ Below 95 target"}</span></div>',
                        unsafe_allow_html=True,
                    )
                    if qs["scores"]:
                        cols = st.columns(5)
                        for i, (label, val) in enumerate(qs["scores"].items()):
                            color = "#15803d" if val >= 9 else "#b45309" if val >= 7 else "#dc2626"
                            with cols[i % 5]:
                                st.markdown(
                                    f'<div class="stat-card">'
                                    f'<div class="stat-value" style="color:{color};font-size:1.2rem;">{val}/10</div>'
                                    f'<div class="stat-label">{label}</div></div>',
                                    unsafe_allow_html=True,
                                )
                    else:
                        st.markdown(parsed["quality_score"])
        else:
            st.markdown('<div style="color:#9ca3af;font-size:0.95rem;padding-top:2rem;">Your production-grade prompt will appear here.</div>', unsafe_allow_html=True)


def main():
    st.markdown('<p class="app-title">⚡ Prompt Optimizer</p>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Optimize existing prompts — or architect new ones from scratch for any AI platform.</p>', unsafe_allow_html=True)

    use_llm, backend, model = render_sidebar()
    groq_key  = _get_groq_key()
    optimizer = get_optimizer()
    extractor = get_extractor()

    tab1, tab2 = st.tabs(["⚡ Prompt Optimizer", "🏗️ PromptArchitect"])

    with tab1:
        left, right = st.columns([1, 1], gap="large")
        with left:
            st.markdown('<p class="section-label">Input</p>', unsafe_allow_html=True)
            uploaded_file = st.file_uploader("Upload file", type=["pdf", "docx", "txt", "md"], label_visibility="collapsed", help="Upload a PDF, Word document, or text file.")
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
            user_input = st.text_area(
                "Paste your prompt", value=prefill, height=420,
                placeholder="Paste your prompt here…\n\nExamples:\n• Claude Code / Cursor / Windsurf instructions\n• ChatGPT or Gemini prompts\n• PRDs, meeting notes, specs, business plans",
                label_visibility="collapsed",
            )
            st.caption(f"{_format_number(len(user_input))} characters · ~{_format_number(len(user_input)//4)} tokens")
            btn_label = "⚡ Optimize with AI" if use_llm else "⚡ Optimize Prompt"
            optimize_clicked = st.button(btn_label, type="primary", use_container_width=True, disabled=not user_input.strip())

        with right:
            st.markdown('<p class="section-label">Optimized Prompt</p>', unsafe_allow_html=True)
            if optimize_clicked and user_input.strip():
                t0 = time.perf_counter()
                optimized_text = None
                used_llm = False
                result = None
                if use_llm and model:
                    if backend == "groq":
                        spinner_msg = f"Running 6-pass optimization with Groq ({model})…"
                    else:
                        spinner_msg = f"Running 6-pass optimization with {model}…"
                    with st.spinner(spinner_msg):
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
                st.session_state["result_text"]    = optimized_text
                st.session_state["original"]       = user_input
                st.session_state["elapsed"]        = elapsed
                st.session_state["used_llm"]       = used_llm
                st.session_state["llm_model"]      = model if used_llm else None
                st.session_state["rule_mode"]      = result["mode"] if result else None
                st.session_state["warnings"]       = result["warnings"] if result else []
                st.session_state["score"]          = result["score"] if result else None
                st.session_state["impossible"]     = result.get("impossible_fixes", []) if result else []
                st.session_state["contradictions"] = result.get("contradictions", []) if result else []

            if "result_text" in st.session_state:
                optimized_text = st.session_state["result_text"]
                original  = st.session_state["original"]
                elapsed   = st.session_state.get("elapsed", 0)
                used_llm  = st.session_state.get("used_llm", False)
                llm_model = st.session_state.get("llm_model") or ""
                rule_mode = st.session_state.get("rule_mode") or "medium"

                if used_llm:
                    pill = '<span class="status-pill status-ai">🤖 AI optimized</span>'
                    model_label = f'<span style="color:#6b7280;font-size:0.8rem;">{llm_model} · {elapsed:.1f}s</span>'
                    st.markdown(f"{pill} &nbsp; {model_label}", unsafe_allow_html=True)
                else:
                    badge = _mode_badge(rule_mode, False)
                    st.markdown(f"Mode: {badge} &nbsp; <span style='color:#6b7280;font-size:0.8rem;'>{elapsed:.2f}s (rule-based)</span>", unsafe_allow_html=True)

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
                    st.download_button("⬇ Download TXT", data=optimized_text, file_name="optimized_prompt.txt", mime="text/plain", use_container_width=True)
                with dl2:
                    st.download_button("⬇ Download Markdown", data=optimized_text, file_name="optimized_prompt.md", mime="text/markdown", use_container_width=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
                st.markdown('<p class="section-label">Statistics</p>', unsafe_allow_html=True)
                stats = calculate_stats(original, optimized_text)
                c1, c2, c3, c4, c5 = st.columns(5)
                with c1:
                    st.markdown(f'<div class="stat-card"><div class="stat-value">{_format_number(stats["original_chars"])}</div><div class="stat-label">Original chars</div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-card"><div class="stat-value">{_format_number(stats["optimized_chars"])}</div><div class="stat-label">Optimized chars</div></div>', unsafe_allow_html=True)
                with c3:
                    removed = stats["chars_removed"]
                    sign = "-" if removed >= 0 else "+"
                    st.markdown(f'<div class="stat-card"><div class="stat-value">{sign}{_format_number(abs(removed))}</div><div class="stat-label">Chars removed</div></div>', unsafe_allow_html=True)
                with c4:
                    pct = stats["reduction_pct"]
                    delta_cls = "stat-delta-good" if pct > 0 else "stat-delta-none"
                    st.markdown(f'<div class="stat-card"><div class="stat-value">{pct:.1f}%</div><div class="{delta_cls}">reduction</div><div class="stat-label">Char reduction</div></div>', unsafe_allow_html=True)
                with c5:
                    t_pct = stats["token_reduction_pct"]
                    t_removed = stats["token_reduction"]
                    delta_cls = "stat-delta-good" if t_pct > 0 else "stat-delta-none"
                    st.markdown(f'<div class="stat-card"><div class="stat-value">{t_pct:.1f}%</div><div class="{delta_cls}">~{_format_number(abs(t_removed))} tokens saved</div><div class="stat-label">Token reduction</div></div>', unsafe_allow_html=True)

                score = st.session_state.get("score")
                if score and not used_llm:
                    st.markdown('<hr class="divider">', unsafe_allow_html=True)
                    st.markdown('<p class="section-label">Quality Score</p>', unsafe_allow_html=True)
                    grade_color = {"A":"#15803d","B":"#1d4ed8","C":"#b45309","D":"#dc2626","F":"#7f1d1d"}.get(score.get("grade","F"),"#6b7280")
                    st.markdown(f'<div style="font-size:2rem;font-weight:700;color:{grade_color};">{score.get("overall",0)}/100 &nbsp; <span style="font-size:1.2rem;">{score.get("grade","?")}</span></div>', unsafe_allow_html=True)
                    dims = [
                        ("Clarity","clarity"),("Specificity","specificity"),
                        ("Hallucination Resist.","hallucination_resistance"),("Research Quality","research_quality"),
                        ("Output Structure","output_structure"),("Token Efficiency","token_efficiency"),
                        ("Contradiction Score","contradiction_score"),("Impossible Req. Score","impossible_requirement_score"),
                    ]
                    cols = st.columns(4)
                    for i, (label, key) in enumerate(dims):
                        val = score.get(key, 0)
                        color = "#15803d" if val >= 8 else "#b45309" if val >= 5 else "#dc2626"
                        with cols[i % 4]:
                            st.markdown(f'<div class="stat-card"><div class="stat-value" style="color:{color};font-size:1.2rem;">{val}/10</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#9ca3af;font-size:0.95rem;padding-top:2rem;">Optimized prompt will appear here.</div>', unsafe_allow_html=True)

    with tab2:
        render_architect_tab(use_llm, backend, model, groq_key)


if __name__ == "__main__":
    main()
