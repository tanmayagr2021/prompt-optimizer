# Prompt Optimizer

A fully local, free Prompt Optimizer that transforms long or inefficient AI prompts into shorter, better-structured ones — without any external APIs, accounts, or configuration.

Works with Claude Code, ChatGPT, Gemini, Cursor, Windsurf, and similar systems.

---

## Quick start

```bash
# 1. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download the spaCy language model
python -m spacy download en_core_web_sm

# 4. Launch the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Optional: faster sentence-transformers (CPU-only PyTorch)

The default `pip install sentence-transformers` pulls a full CUDA-capable PyTorch build (~2 GB). For CPU-only machines:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
```

The app works without `sentence-transformers` — it falls back to keyword-based redundancy detection automatically.

---

## How it works

| Mode   | Triggered when          | Strategy                                            |
|--------|-------------------------|-----------------------------------------------------|
| Small  | < 500 characters        | Cleanup + minor phrase enhancement                  |
| Medium | 500 – 3,000 characters  | Cleanup + dedup + role/stack extraction + reformat  |
| Large  | > 3,000 characters      | Full spec generation (Objective / Users / Features / Stack / Constraints / Deliverables) |

The mode is chosen automatically. The user never sees or configures it.

### Pipeline steps

1. **Cleanup** — strips HTML, normalises whitespace, removes decorative markdown, deduplicates exact lines
2. **Intent analysis** — extracts role, task, tech stack, constraints, users, features, and objective
3. **Redundancy removal** — semantic dedup via sentence-transformers, or keyword-based synonym-group dedup
4. **Restructuring** — converts role prose to `**Role:**` blocks, inline tech stacks to `**Stack:**` bullet lists, prose comma-lists to bullet points
5. **Constraint enforcement** — any critical constraints (do not / must not / preserve / maintain) that were removed are re-injected into the output
6. **Enhancement** — replaces vague phrases ("make a website") with clearer ones ("Build a production-ready website") using a curated, high-confidence lookup table

---

## Supported input types

### Text input
Paste any prompt directly into the text area.

### File upload
| Format | Method          |
|--------|-----------------|
| `.pdf` | MarkItDown      |
| `.docx`| MarkItDown      |
| `.txt` | Direct decode   |
| `.md`  | Direct decode   |

---

## Project structure

```
app.py          — Streamlit UI (single page)
optimizer.py    — Core pipeline (cleanup → dedup → restructure → spec)
analyzer.py     — Intent analysis (role, task, tech stack, constraints, doc type)
extractor.py    — File extraction via MarkItDown
utils.py        — Stats, token estimation, text helpers
requirements.txt
README.md
```

---

## Dependencies

| Library              | Purpose                          |
|----------------------|----------------------------------|
| streamlit            | UI                               |
| markitdown           | PDF / DOCX extraction            |
| spacy                | NLP (lazy-loaded, optional)      |
| sentence-transformers| Semantic redundancy detection    |
| nltk                 | Tokenisation fallback            |

All dependencies are free and open-source. No external AI APIs are used.
