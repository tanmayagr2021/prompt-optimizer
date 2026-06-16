# ⚡ Prompt Optimizer

Compress and restructure AI prompts — removes filler, strips redundancy, and produces structured outputs that get better results from ChatGPT, Claude, Gemini, Cursor, and more.

Runs **100% locally**. No API key. No account. No cost.

---

## Install (macOS) — one command

Open **Terminal** and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/tanmayagr2021/prompt-optimizer/main/install.sh | bash
```

That's it. The script installs everything and puts **PromptOptimizer.app** on your Desktop. Double-click to launch.

> **First time macOS blocks it?** Right-click the app → **Open** → click **Open** in the dialog. Only needed once.

---

## Optional: enable AI mode (free, local)

The default optimizer uses rules. For dramatically better results, add a local AI in ~5 minutes:

1. Download **Ollama** → [ollama.com/download](https://ollama.com/download)
2. Open Terminal and run:
   ```bash
   ollama pull llama3.2
   ```
3. Relaunch the app — the sidebar shows **🟢 Ollama connected** and AI mode turns on automatically.

No API key. No cost. Fully private — the model runs on your Mac.

---

## How it works

Paste any prompt → click **⚡ Optimize** → get a shorter, sharper version.

| Prompt type | What it produces |
|---|---|
| Technical (build / create) | Task · Stack · Requirements · Output Format |
| Research / analysis | Research Question · Evidence Standards · Hallucination guardrails · Report structure |
| Code review | Role · Focus Areas · Severity-ranked output format · Flags missing code |
| Small / conversational | Filler stripped, vague phrases sharpened |

### What gets removed
- Polite filler: *"please"*, *"I would like you to"*, *"could you"*, *"I want you to"*
- Hedging: *"I think"*, *"maybe"*, *"sort of"*, *"I believe"*
- Weak intensifiers: *"very"*, *"really"*, *"quite"*, *"basically"*
- Verbose phrases: *"in order to"* → **to**, *"make use of"* → **use**, *"has the ability to"* → **can**

---

## Supported input

- Paste any text directly
- Upload **PDF**, **DOCX**, **TXT**, or **MD** files

---

## Update to latest version

Re-run the same install command:

```bash
curl -fsSL https://raw.githubusercontent.com/tanmayagr2021/prompt-optimizer/main/install.sh | bash
```

---

## Manual setup (if you prefer)

```bash
git clone https://github.com/tanmayagr2021/prompt-optimizer.git
cd prompt-optimizer
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## Project structure

```
app.py           — Streamlit UI
optimizer.py     — Rule-based pipeline (cleanup → dedup → structure)
analyzer.py      — Intent analysis (role, task, tech stack, constraints)
llm_backend.py   — Ollama AI backend
extractor.py     — PDF / DOCX text extraction
utils.py         — Stats and helpers
menubar_app.py   — macOS menu bar launcher
install.sh       — One-line installer
```
